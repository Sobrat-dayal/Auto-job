"""Windows Media OCR integration and text target matching (Stage 18)."""

import asyncio
from difflib import SequenceMatcher
import io
import logging
import time
from PIL import Image
from app.visual.contracts import BoundingBox, OCRLine, OCRResult, OCRWord

logger = logging.getLogger("autonom.visual.grounding.ocr")


class WindowsMediaOCREngine:
    """Offline high-performance OCR engine powered by Windows 10/11 native WinRT OCR."""

    def __init__(self) -> None:
        self._engine: Any = None
        self._init_engine()

    def _init_engine(self) -> None:
        try:
            import winsdk.windows.media.ocr as ocr
            self._engine = ocr.OcrEngine.try_create_from_user_profile_languages()
            if not self._engine:
                # Fallback to en-US
                import winsdk.windows.globalization as glob
                self._engine = ocr.OcrEngine.try_create_from_language(glob.Language("en-US"))
            logger.info("Windows Media OCR Engine initialized successfully")
        except Exception as e:
            logger.warning(f"Windows Media OCR Engine unavailable: {e}")
            self._engine = None

    @property
    def is_available(self) -> bool:
        return self._engine is not None

    async def extract_text_from_image(self, image: Image.Image) -> OCRResult:
        """Asynchronously extracts all text lines and bounding boxes from a Pillow Image."""
        if not self._engine:
            return OCRResult(text="", lines=[], duration_ms=0.0)

        start_time = time.perf_counter()

        try:
            import winsdk.windows.graphics.imaging as imaging
            import winsdk.windows.storage.streams as streams

            # Ensure image is in RGBA mode
            rgba_img = image.convert("RGBA")
            buf = io.BytesIO()
            rgba_img.save(buf, format="PNG")
            raw_bytes = buf.getvalue()

            # Feed to WinRT stream
            mem_stream = streams.InMemoryRandomAccessStream()
            writer = streams.DataWriter(mem_stream)
            writer.write_bytes(raw_bytes)
            await writer.store_async()
            await writer.flush_async()
            writer.detach_stream()
            mem_stream.seek(0)

            decoder = await imaging.BitmapDecoder.create_async(mem_stream)
            soft_bmp = await decoder.get_software_bitmap_async()

            res = await self._engine.recognize_async(soft_bmp)

            extracted_lines: list[OCRLine] = []
            for line in res.lines:
                words: list[OCRWord] = []
                for w in line.words:
                    rect = w.bounding_rect
                    word_box = BoundingBox(
                        left=int(rect.x),
                        top=int(rect.y),
                        width=max(1, int(rect.width)),
                        height=max(1, int(rect.height)),
                    )
                    words.append(OCRWord(text=w.text, bounding_box=word_box, confidence=1.0))

                line_rect = line.words[0].bounding_rect if line.words else None
                if line.words:
                    min_x = min(int(w.bounding_rect.x) for w in line.words)
                    min_y = min(int(w.bounding_rect.y) for w in line.words)
                    max_r = max(int(w.bounding_rect.x + w.bounding_rect.width) for w in line.words)
                    max_b = max(int(w.bounding_rect.y + w.bounding_rect.height) for w in line.words)
                    line_box = BoundingBox(left=min_x, top=min_y, width=max_r - min_x, height=max_b - min_y)
                else:
                    line_box = BoundingBox(left=0, top=0, width=0, height=0)

                extracted_lines.append(OCRLine(text=line.text, words=words, bounding_box=line_box))

            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return OCRResult(text=res.text or "", lines=extracted_lines, duration_ms=duration_ms)

        except Exception as e:
            logger.error(f"OCR recognition error: {e}")
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return OCRResult(text="", lines=[], duration_ms=duration_ms)

    def find_text_targets(
        self,
        ocr_result: OCRResult,
        query: str,
        exact: bool = False,
        min_similarity: float = 0.8,
    ) -> list[tuple[str, BoundingBox, float]]:
        """Searches OCR lines and words for query matches. Returns list of (matched_text, box, score)."""
        matches: list[tuple[str, BoundingBox, float]] = []
        q = query.strip()
        q_lower = q.lower()

        # Check line-level matches first
        for line in ocr_result.lines:
            line_text = line.text.strip()
            line_lower = line_text.lower()

            if exact and line_text == q:
                matches.append((line_text, line.bounding_box, 1.0))
            elif not exact and q_lower in line_lower:
                score = round(len(q_lower) / float(len(line_lower)), 2)
                matches.append((line_text, line.bounding_box, max(0.9, score)))
            elif not exact and min_similarity > 0:
                sim = SequenceMatcher(None, q_lower, line_lower).ratio()
                if sim >= min_similarity:
                    matches.append((line_text, line.bounding_box, round(sim, 2)))

        # If no line matches, search individual words
        if not matches:
            for line in ocr_result.lines:
                for w in line.words:
                    w_text = w.text.strip()
                    w_lower = w_text.lower()
                    if exact and w_text == q:
                        matches.append((w_text, w.bounding_box, 1.0))
                    elif not exact and (q_lower == w_lower or q_lower in w_lower):
                        matches.append((w_text, w.bounding_box, 0.95))
                    elif not exact and min_similarity > 0:
                        sim = SequenceMatcher(None, q_lower, w_lower).ratio()
                        if sim >= min_similarity:
                            matches.append((w_text, w.bounding_box, round(sim, 2)))

        # Sort matches by similarity score descending
        matches.sort(key=lambda m: m[2], reverse=True)
        return matches


ocr_engine = WindowsMediaOCREngine()

