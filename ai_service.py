import os
import logging
import time
import json
import re

from groq import Groq

from schemas import Lead
from prompts import PROMPTS

from typing import Optional


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"
        self.prompts = PROMPTS

    def _initialize_prompts(self) -> dict:
      # prompts are now provided by the external module 'prompts'
      pass

    def _contains_profanity(self, text: str) -> bool:
        normalized = (text or "").lower()
        profanity_patterns = self._profanity_patterns()
        return any(re.search(pattern, normalized, re.IGNORECASE) for pattern in profanity_patterns)

    def _profanity_patterns(self) -> tuple[str, ...]:
        # Lightweight profanity detector (PL). Intentionally conservative.
        return (
            r"\bkurw\w*\b",
            r"\bchuj\w*\b",
            r"\bjeb\w*\b",
            r"\bpierdol\w*\b",
            r"\bskurw\w*\b",
            r"\bspierdol\w*\b",
        )

    def _remove_profanity_terms(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return text

        sanitized = text
        for pattern in self._profanity_patterns():
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()
        sanitized = re.sub(r"\s+([,.;:!?])", r"\1", sanitized)
        return sanitized

    def _fix_common_summary_typos(self, summary: Optional[str]) -> Optional[str]:
        if not summary:
            return summary

        fixed = summary
        fixed = re.sub(r"fotowoltaj", "fotowoltaic", fixed, flags=re.IGNORECASE)
        fixed = re.sub(r"fotowoltai", "fotowoltaic", fixed, flags=re.IGNORECASE)
        fixed = fixed.strip()
        if fixed and fixed[0].islower():
            fixed = fixed[0].upper() + fixed[1:]
        if fixed and fixed[-1] not in ".!?":
            fixed += "."
        return fixed

    def _postprocess_lead(self, lead: Lead, source_text: str) -> Lead:
      if self._contains_profanity(source_text):
        lead.summary = self._remove_profanity_terms(lead.summary)

      lead.summary = self._fix_common_summary_typos(lead.summary)

      if self._contains_profanity(source_text):
        note = "Wiadomość zawiera wulgarny język."
        if lead.summary:
          if note.lower() not in lead.summary.lower():
            lead.summary = lead.summary.rstrip(" .") + ". " + note
        else:
          lead.summary = note

        if isinstance(lead.score, int) and lead.score > 1:
          lead.score = max(1, lead.score - 1)

      # Ensure neutral summary for off-topic leads (score <= 2)
      try:
        if isinstance(lead.score, int) and lead.score <= 2:
          neutral = "Zapytanie poza zakresem oferty."
          # Preserve profanity note if present
          if lead.summary and "wulgarny" in lead.summary.lower():
            # Keep only the note
            lead.summary = neutral + " Wiadomość zawiera wulgarny język."
          else:
            lead.summary = neutral
      except Exception:
        pass

      # Sanitize name: only accept likely personal names; otherwise set to None
      try:
        lead.name = self._sanitize_name(lead.name)
      except Exception:
        lead.name = None

      # Backfill email/phone from source text if missing
      try:
        if not lead.email:
          lead.email = self._extract_email(source_text)
      except Exception:
        pass
      try:
        if not lead.phone:
          lead.phone = self._extract_phone(source_text)
      except Exception:
        pass

      return lead

    def _sanitize_name(self, name: Optional[str]) -> Optional[str]:
      if not name:
        return None
      s = name.strip()
      if not s:
        return None
      if len(s) > 60:
        return None
      if any(ch.isdigit() for ch in s):
        return None
      if "@" in s:
        return None
      s_l = s.lower()
      noise_keywords = (
        "pokoi", "pokoj", "pokoje", "wyceny", "wycena", "grupy", "grupa", "osób", "osoby", "osoba",
        "tydzie", "dla", "proszę", "prosze", "rezerwac", "nocleg", "hotel", "klimatyz", "fotowolt",
        "pompa", "rekuper", "budżet", "budzet", "termin", "ofert"
      )
      if any(k in s_l for k in noise_keywords):
        return None
      # Accept names like Jan, Jan Kowalski, Jan A. Kowalski (basic heuristic)
      name_regex = re.compile(r"^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+( [A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\.]+){0,2}$")
      if name_regex.match(s):
        return s
      return None

    def _extract_email(self, text: str) -> Optional[str]:
      if not text:
        return None
      m = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
      return m.group(0) if m else None

    def _extract_phone(self, text: str) -> Optional[str]:
      if not text:
        return None
      m = re.search(r"\+?\d[\d\s\-()]{6,}\d", text)
      return m.group(0).strip() if m else None

    def process_lead_text(self, text: str) -> Lead:
        """Default entrypoint: auto-detect niche based on text."""
        niche = self._detect_niche(text)
        return self.process_lead_niche(text, niche=niche)

    def _detect_niche(self, text: str) -> str:
        """Lightweight router so '/process-lead' works without passing niche explicitly."""
        normalized = (text or "").lower()

        # Hotel/hospitality keywords
        hotel_keywords = (
            "hotel",
            "nocleg",
            "pokój",
            "pokoje",
            "pokoj",
            "pokoi",
            "rezerwacj",
            "zakwaterowanie",
            "konferencj",
            "event",
        )
        if any(keyword in normalized for keyword in hotel_keywords):
            return "hotelarstwo"

        # HVAC keywords
        hvac_keywords = (
            "klimatyz",
            "klimatyzator",
            "klima",
            "split",
            "multisplit",
            "rekuper",
            "rekuperator",
            "wentyl",
            "hvac",
        )
        if any(keyword in normalized for keyword in hvac_keywords):
            return "klimatyzacja_rekuperacja"

        return "fotowoltaika_pompy_ciepla"

    def process_lead_niche(self, text: str, niche: str = "fotowoltaika_pompy_ciepla") -> Lead:
        """
        Process lead text with niche-specific prompt.
        
        Available niches: fotowoltaika_pompy_ciepla, klimatyzacja_rekuperacja
        """
        # Validate niche
        if niche not in self.prompts:
            logger.warning(f"Unknown niche '{niche}', using default 'fotowoltaika_pompy_ciepla'")
            niche = "fotowoltaika_pompy_ciepla"
        
        # Build prompt with user text
        prompt = f"""{self.prompts[niche]}

        IMPORTANT OUTPUT RULES:
        - Return ONLY a single JSON object. No markdown, no commentary, no backticks.
        - The JSON MUST contain exactly these keys:
          name, company, email, phone, product, budget_est, urgency, city, summary, score
        - Use null (without quotes) for unknown/missing values.
        - Do NOT invent email/phone. If not present, set to null.
        - score is REQUIRED and MUST be an integer from 1 to 10.
        - summary MUST be in Polish, 1 sentence, correct grammar and spacing; fix obvious typos (e.g. missing spaces).
        - summary should be human-readable (not copied raw); include the requested product/service and any numbers/budget mentioned.
        - NEVER include profanity/vulgar words in the summary (do not quote them).

        INPUT TEXT:
        "{text}"

        OUTPUT JSON:
        """

        max_retries = 3
        for attempt in range(max_retries):
          raw_content = None
          try:
            logger.info(f"Processing lead text, attempt {attempt + 1}")
            response = self.client.chat.completions.create(
              messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem, który zawsze zwraca prawidłowy JSON."},
                {"role": "user", "content": prompt}
              ],
              model=self.model,
              temperature=0.1,  # Niska temperatura dla spójności
              max_tokens=500
            )

            raw_content = response.choices[0].message.content.strip()

            # Remove possible markdown ```json
            if raw_content.startswith("```json"):
              raw_content = raw_content[7:]
            if raw_content.endswith("```"):
              raw_content = raw_content[:-3]
            raw_content = raw_content.strip()

            # Try to find JSON object if extra text exists
            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if json_match:
              raw_content = json_match.group(0)

            data = json.loads(raw_content)

            # Validate with Pydantic
            lead = Lead(**data)
            lead = self._postprocess_lead(lead, text)
            logger.info("Successfully processed lead")
            return lead
          except Exception as e:
            logger.exception(f"Error during AI processing on attempt {attempt + 1}: {str(e)}")
            if raw_content:
              logger.error(f"Raw AI content (truncated): {raw_content[:2000]}")
            if attempt < max_retries - 1:
              time.sleep(1)  # Wait before retry
            else:
              logger.error("All retries failed, returning manual verification lead")
              # Return a lead indicating manual verification needed
              return Lead(
                name=None,
                company=None,
                email=None,
                phone=None,
                product=None,
                budget_est=None,
                urgency=None,
                city=None,
                summary="Requires manual verification - AI processing failed",
                score=1
              )
