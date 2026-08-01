"""The same facts, spelled out in words instead of digits.

The bundled benchmark's document writes every quantity as an Arabic
numeral: "412 units", "7 consecutive... days", "3 percent", "30 days".
``_score_tokens``'s digit bonus (+0.5 surprise for any token containing a
digit character) means every one of those numbers is protected from
compression. It says nothing about a document that expresses the same
facts in prose, which is exactly as common in real contracts, emails, and
transcripts: "four hundred twelve units", "seven consecutive... days",
"three percent", "thirty days". None of those get the digit bonus, so
they compress away at the exact ratio the original benchmark calls safe.

``ADVERSARIAL_DOCUMENT`` restates ``corpus.DOCUMENT`` fact-for-fact with
every number spelled out, so any recall difference between the two is
attributable purely to numeral style, not different content.
"""
from __future__ import annotations

ADVERSARIAL_DOCUMENT = (
    "In accordance with the terms outlined in this agreement, it is important "
    "to note that the vendor shall deliver the completed hardware shipment, "
    "which consists of exactly four hundred twelve units of the model RX9000 "
    "industrial sensor, to the designated warehouse located in Rotterdam no "
    "later than the fifteenth of March. It should also be mentioned that, as "
    "a general matter of company policy, any delay that exceeds a period of "
    "seven consecutive calendar days will automatically trigger a "
    "contractual penalty clause amounting to a reduction of three percent "
    "of the total invoice value, which currently stands at one point two "
    "million dollars. Furthermore, in the event that the shipment is "
    "delayed beyond thirty days in total, the buyer, Meridian Logistics, "
    "reserves the right to unilaterally terminate the agreement without "
    "further notice or any additional financial liability whatsoever being "
    "incurred by either of the two parties involved in this transaction."
)

ADVERSARIAL_QUESTIONS: list[tuple[str, list[str]]] = [
    ("how many units and what model", ["twelve", "rx9000"]),
    ("where does it ship and by when", ["rotterdam", "march"]),
    ("what triggers the penalty and how much", ["seven", "three", "percent"]),
    ("who can terminate and at what delay", ["meridian", "thirty"]),
]

# A second, independently-written word-form document (a different domain, a
# project status update instead of a contract), written after compress_v2's
# number-word list was frozen against ADVERSARIAL_DOCUMENT above. Evaluated
# exactly once.
HOLDOUT_DOCUMENT = (
    "The engineering team completed the migration ahead of the original "
    "estimate. Out of the fifty three services that needed to move, forty "
    "eight have already been cut over to the new cluster, and the remaining "
    "five are scheduled for next week. The rollback window is seventy two "
    "hours after each cutover, during which any service can be reverted "
    "without a formal incident review. Overall error rates increased by "
    "less than one percent during the transition, well inside the two "
    "percent threshold the team had agreed on beforehand. The project lead, "
    "Priya Desai, will present the final results at the twenty second "
    "quarterly review."
)

HOLDOUT_QUESTIONS: list[tuple[str, list[str]]] = [
    ("how many services moved and how many are left", ["forty", "eight", "five"]),
    ("how long is the rollback window", ["seventy", "two", "hours"]),
    ("what was the acceptable error threshold", ["two", "percent"]),
    ("who is presenting and when", ["priya", "desai", "twenty", "second"]),
]
