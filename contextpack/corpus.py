"""A document with known load-bearing keywords per question.

Each entry is a chunk of realistic, wordy prose (the kind that eats your context
window) plus the specific keywords a downstream question needs answered
correctly. If those keywords survive compression, the answer is still
recoverable. If they do not, compression broke the thing that mattered.
"""
from __future__ import annotations

DOCUMENT = (
    "In accordance with the terms outlined in this agreement, it is important "
    "to note that the vendor shall deliver the completed hardware shipment, "
    "which consists of exactly 412 units of the model RX9000 industrial "
    "sensor, to the designated warehouse located in Rotterdam no later than "
    "the fifteenth of March. It should also be mentioned that, as a general "
    "matter of company policy, any delay that exceeds a period of 7 "
    "consecutive calendar days will automatically trigger a contractual "
    "penalty clause amounting to a reduction of 3 percent of the total "
    "invoice value, which currently stands at 1200000 dollars. Furthermore, "
    "in the event that the shipment is delayed beyond 30 days in total, the "
    "buyer, Meridian Logistics, reserves the right to unilaterally terminate "
    "the agreement without further notice or any additional financial "
    "liability whatsoever being incurred by either of the two parties "
    "involved in this transaction."
)

# (question, required_keywords). Keywords are the load-bearing content: the
# specific numbers, names, and terms an answer to the question needs. Each one
# is verified to appear as an exact token in DOCUMENT (see tests).
QUESTIONS: list[tuple[str, list[str]]] = [
    ("how many units and what model", ["412", "rx9000"]),
    ("where does it ship and by when", ["rotterdam", "march"]),
    ("what triggers the penalty and how much", ["7", "3", "percent"]),
    ("what is the total invoice value", ["1200000"]),
    ("who can terminate and at what delay", ["meridian", "30"]),
]
