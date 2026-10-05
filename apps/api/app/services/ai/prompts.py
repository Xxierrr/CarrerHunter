"""
Prompt templates for Gemini AI calls.
Each prompt is carefully designed to produce structured JSON output.
Prompts never ask Gemini to fabricate information.
"""

EXTRACT_REQUIREMENTS_PROMPT = """You are analyzing a job/internship posting to extract structured requirements.

RULES:
- Extract ONLY what is explicitly stated or strongly implied in the posting
- Do NOT invent or assume requirements not mentioned
- If something is unclear, set confidence lower
- Include the source text snippet for each requirement you extract

Job Title: {title}

Job Description:
{description}

Extract the following structured information as JSON:
{{
  "role_title": "cleaned title",
  "role_category": "one of: software_engineering, data_science, ml_ai, product, design, marketing, finance, research, other",
  "skills_required": ["skill1", "skill2"],
  "skills_preferred": ["skill1"],
  "technologies": ["tech1", "tech2"],
  "degree": {{
    "required": true/false,
    "level": "bachelors/masters/phd/any or null",
    "fields": ["field1", "field2"],
    "source_text": "exact quote from posting"
  }},
  "graduation": {{
    "minimum_year": 2026 or null,
    "maximum_year": 2028 or null,
    "must_be_enrolled": true/false/null,
    "source_text": "exact quote"
  }},
  "experience": {{
    "required": true/false,
    "minimum_years": 0 or null,
    "type": "professional/internship/academic/any or null",
    "details": "description",
    "source_text": "exact quote"
  }},
  "work_authorization": {{
    "required": true/false,
    "countries": ["US", "UK"],
    "visa_sponsorship": true/false/null,
    "details": "description",
    "source_text": "exact quote"
  }},
  "gpa_minimum": 3.0 or null,
  "remote_status": "remote/hybrid/onsite/unknown",
  "duration_weeks": 12 or null,
  "location": "City, State/Country",
  "country": "country code or name",
  "salary_info": "if mentioned",
  "application_deadline": "date if mentioned",
  "key_responsibilities": ["resp1", "resp2"],
  "confidence": 0.0-1.0
}}
"""

CLASSIFY_ROLE_PROMPT = """Classify this internship role.

Title: {title}
Description (first 500 chars): {description}

Return JSON:
{{
  "category": "one of: software_engineering, data_science, ml_ai, product, design, marketing, finance, research, operations, consulting, other",
  "subcategory": "more specific category or null",
  "seniority": "intern",
  "domain": "industry domain or null",
  "confidence": 0.0-1.0
}}
"""

EXPLAIN_ELIGIBILITY_PROMPT = """You are explaining a candidate's eligibility for an internship.

RULES:
- Be honest and objective
- Do NOT fabricate or exaggerate the candidate's qualifications
- If uncertain, say "uncertain" rather than guessing
- Base everything on the provided information only

Candidate Summary:
{candidate_summary}

Job Requirements:
{job_summary}

Eligibility Criteria Results:
{criteria}

Write a brief, clear explanation (2-4 sentences) of the candidate's overall eligibility.
Mention key strengths and potential gaps. If any requirements are unclear, note that.
"""

GENERATE_COVER_LETTER_PROMPT = """Generate a professional cover letter for an internship application.

CRITICAL RULES:
- Use ONLY the verified information provided below
- NEVER fabricate experiences, projects, skills, or achievements
- NEVER add information not present in the candidate profile
- Keep it concise (250-350 words)
- Be genuine and professional

Candidate Profile:
{candidate_summary}

Job Details:
{job_summary}

Write a tailored cover letter that:
1. Opens with genuine interest in the role
2. Highlights relevant skills and experiences FROM THE PROFILE ONLY
3. Connects candidate's background to job requirements
4. Closes professionally
"""

PARSE_RESUME_PROMPT = """Extract structured information from this resume text.

RULES:
- Extract only what is explicitly present
- Do not infer or add information
- Preserve original formatting of names, titles, etc.

Resume Text:
{resume_text}

Return JSON:
{{
  "name": "full name or null",
  "email": "email or null",
  "phone": "phone or null",
  "education": [
    {{"institution": "name", "degree": "degree", "field": "major", "gpa": "gpa or null", "graduation_date": "date or null"}}
  ],
  "skills": ["skill1", "skill2"],
  "programming_languages": ["lang1", "lang2"],
  "frameworks": ["framework1"],
  "projects": [
    {{"title": "name", "description": "brief desc", "technologies": ["tech1"]}}
  ],
  "experience": [
    {{"title": "role", "organization": "company", "duration": "dates", "description": "brief desc"}}
  ],
  "certifications": ["cert1"],
  "links": {{"github": "url", "linkedin": "url", "portfolio": "url"}}
}}
"""
