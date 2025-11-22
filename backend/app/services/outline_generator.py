import os
import json
from typing import List, Dict
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OutlineGenerator:

    def _generate_outline_for_chunk(self, text: str) -> Dict:
        SYSTEM_MSG = """
        You are a senior curriculum designer. Extract structured educational metadata
        from this chunk of text.

        Return strictly valid JSON:
        {
          "topics": [string],
          "subtopics": { topic: [subtopic list] },
          "key_concepts": [string],
          "definitions": { term: definition }
        }

        Absolutely no made-up topics or terms.
        Only return what is explicitly present or strongly implied.
        """

        USER_MSG = f"Extract outline components from this text:\n\n{text[:15000]}"

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": USER_MSG}
            ],
            temperature=0.1
        )

        raw = response.choices[0].message.content

        try:
            return json.loads(raw)
        except:
            json_str = raw[raw.index("{"): raw.rindex("}")+1]
            return json.loads(json_str)


    def _merge_outlines(self, outlines: List[Dict]) -> Dict:
        merged = {
            "topics": [],
            "subtopics": {},
            "key_concepts": [],
            "definitions": {}
        }

        for o in outlines:
            # merge topics
            for t in o["topics"]:
                if t not in merged["topics"]:
                    merged["topics"].append(t)

            # merge subtopics
            for topic, subs in o.get("subtopics", {}).items():
                if topic not in merged["subtopics"]:
                    merged["subtopics"][topic] = []

                for s in subs:
                    if s not in merged["subtopics"][topic]:
                        merged["subtopics"][topic].append(s)

            # merge key concepts
            for k in o["key_concepts"]:
                if k not in merged["key_concepts"]:
                    merged["key_concepts"].append(k)

            # merge definitions
            for term, definition in o["definitions"].items():
                if term not in merged["definitions"]:
                    merged["definitions"][term] = definition

        return merged


    def _generate_global_order(self, merged: Dict) -> List[str]:
        SYSTEM_MSG = """
        You are an expert educator. Based on the topics extracted, produce a logical
        teaching order that progresses from beginner → intermediate → advanced.

        Return JSON:
        { "order": [topic1, topic2, ...] }
        """

        USER_MSG = f"Topics: {merged['topics']}"

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": USER_MSG}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content
        return json.loads(raw)["order"]


    def generate_outline(self, chunks: List[str]) -> Dict:
        per_chunk_outlines = [
            self._generate_outline_for_chunk(chunk) 
            for chunk in chunks
        ]

        merged = self._merge_outlines(per_chunk_outlines)
        merged["suggested_order"] = self._generate_global_order(merged)

        return merged
