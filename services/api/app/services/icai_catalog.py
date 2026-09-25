"""Official ICAI study-material index.

The app stores only titles and official links. It does not mirror ICAI PDFs; every
card sends the learner to the source published by ICAI, respecting the notice on
the source page.
"""

ICAI_CATALOG: tuple[dict[str, str], ...] = (
    {"level": "CA Foundation", "subject": "Accounting", "chapter": "Module 1 · Theoretical Framework and Accounting Process", "title": "Foundation Paper 1 · Accounting · Module 1", "source": "https://www.icai.org/post/sm-foundation-p1-may2027"},
    {"level": "CA Foundation", "subject": "Accounting", "chapter": "Module 2 · Partnership and Company Accounts", "title": "Foundation Paper 1 · Accounting · Module 2", "source": "https://www.icai.org/post/sm-foundation-p1-may2027"},
    {"level": "CA Foundation", "subject": "Business Laws", "chapter": "Complete paper and latest applicable material", "title": "Foundation Paper 2 · Business Laws", "source": "https://www.icai.org/post/sm-foundation-paper2"},
    {"level": "CA Foundation", "subject": "Quantitative Aptitude", "chapter": "Complete paper and latest applicable material", "title": "Foundation Paper 3 · Quantitative Aptitude", "source": "https://www.icai.org/post/sm-foundation-paper3"},
    {"level": "CA Foundation", "subject": "Business Economics", "chapter": "Complete paper and latest applicable material", "title": "Foundation Paper 4 · Business Economics", "source": "https://www.icai.org/post/sm-foundation-paper4"},
    {"level": "CA Foundation", "subject": "Model Test Papers", "chapter": "Foundation model test papers", "title": "Foundation · Model Test Papers", "source": "https://resource.cdn.icai.org/84774bos68243.pdf"},
    {"level": "CA Intermediate", "subject": "Advanced Accounting", "chapter": "Module 1 · Accounting Standards", "title": "Intermediate Paper 1 · Advanced Accounting · Module 1", "source": "https://www.icai.org/post/bos-int-p1-may2027-exam"},
    {"level": "CA Intermediate", "subject": "Advanced Accounting", "chapter": "Module 2 · Assets, liabilities and consolidation", "title": "Intermediate Paper 1 · Advanced Accounting · Module 2", "source": "https://www.icai.org/post/bos-int-p1-may2027-exam"},
    {"level": "CA Intermediate", "subject": "Advanced Accounting", "chapter": "Module 3 · Company financial statements", "title": "Intermediate Paper 1 · Advanced Accounting · Module 3", "source": "https://www.icai.org/post/bos-int-p1-may2027-exam"},
    {"level": "CA Intermediate", "subject": "Corporate and Other Laws", "chapter": "Companies Act and other laws", "title": "Intermediate Paper 2 · Corporate and Other Laws", "source": "https://www.icai.org/post/sm-intermediate-paper2"},
    {"level": "CA Intermediate", "subject": "Taxation", "chapter": "Section A · Income-tax Law", "title": "Intermediate Paper 3 · Taxation · Income-tax Law", "source": "https://www.icai.org/post/sm-intermediate-paper3-seca"},
    {"level": "CA Intermediate", "subject": "Taxation", "chapter": "Section B · Goods and Services Tax", "title": "Intermediate Paper 3 · Taxation · GST", "source": "https://www.icai.org/post/sm-intermediate-paper3-secb"},
    {"level": "CA Intermediate", "subject": "Cost and Management Accounting", "chapter": "Complete paper and latest applicable material", "title": "Intermediate Paper 4 · Cost and Management Accounting", "source": "https://www.icai.org/post/sm-intermediate-paper4"},
    {"level": "CA Intermediate", "subject": "Auditing and Ethics", "chapter": "Complete paper and latest applicable material", "title": "Intermediate Paper 5 · Auditing and Ethics", "source": "https://www.icai.org/post/sm-intermediate-paper5"},
    {"level": "CA Intermediate", "subject": "Financial Management", "chapter": "Section A · Financial Management", "title": "Intermediate Paper 6 · Financial Management", "source": "https://www.icai.org/post/sm-intermediate-paper6a"},
    {"level": "CA Intermediate", "subject": "Strategic Management", "chapter": "Section B · Strategic Management", "title": "Intermediate Paper 6 · Strategic Management", "source": "https://www.icai.org/post/sm-intermediate-paper6b"},
    {"level": "CA Intermediate", "subject": "Model Test Papers", "chapter": "Intermediate Group 1 and Group 2", "title": "Intermediate · Model Test Papers", "source": "https://resource.cdn.icai.org/84775bos68244-gp1.pdf"},
    {"level": "CA Final", "subject": "Financial Reporting", "chapter": "Group I · Paper 1", "title": "Final Paper 1 · Financial Reporting", "source": "https://www.icai.org/post/sm-final-paper1"},
    {"level": "CA Final", "subject": "Advanced Financial Management", "chapter": "Group I · Paper 2", "title": "Final Paper 2 · Advanced Financial Management", "source": "https://www.icai.org/post/sm-final-paper2"},
    {"level": "CA Final", "subject": "Advanced Auditing", "chapter": "Group I · Paper 3", "title": "Final Paper 3 · Advanced Auditing and Assurance", "source": "https://www.icai.org/post/sm-final-paper3"},
    {"level": "CA Final", "subject": "Direct Tax Laws", "chapter": "Group II · Paper 4", "title": "Final Paper 4 · Direct Tax Laws and International Taxation", "source": "https://www.icai.org/post/sm-final-paper4"},
    {"level": "CA Final", "subject": "Indirect Tax Laws", "chapter": "Group II · Paper 5", "title": "Final Paper 5 · Indirect Tax Laws", "source": "https://www.icai.org/post/sm-final-paper5"},
    {"level": "CA Final", "subject": "Integrated Business Solutions", "chapter": "Group II · Paper 6", "title": "Final Paper 6 · Integrated Business Solutions", "source": "https://www.icai.org/post.html?post_id=19442"},
    {"level": "CA Final", "subject": "Model Test Papers", "chapter": "Group I", "title": "Final · Model Test Papers · Group I", "source": "https://resource.cdn.icai.org/84556bos68130-final-gp1.pdf"},
    {"level": "CA Final", "subject": "Model Test Papers", "chapter": "Group II", "title": "Final · Model Test Papers · Group II", "source": "https://resource.cdn.icai.org/84557bos68130-final-gp2.pdf"},
    {"level": "CA Final", "subject": "SPOM · Set A", "chapter": "Corporate and Economic Laws", "title": "Self-Paced Online Modules · Set A", "source": "https://www.icai.org/post/bos-exam-spom-set-a"},
    {"level": "CA Final", "subject": "SPOM · Set B", "chapter": "Strategic Cost and Performance Management", "title": "Self-Paced Online Modules · Set B", "source": "https://www.icai.org/post/self-paced-online-modules-set-b-nset"},
    {"level": "CA Final", "subject": "SPOM · Set C", "chapter": "Risk Management, Sustainability, Public Finance and specialised papers", "title": "Self-Paced Online Modules · Set C", "source": "https://www.icai.org/post/self-paced-online-modules-nset"},
    {"level": "CA Final", "subject": "SPOM · Set D", "chapter": "Constitution, Psychology, Entrepreneurship and Digital Ecosystem", "title": "Self-Paced Online Modules · Set D", "source": "https://www.icai.org/post/self-paced-online-modules-nset"},
)
