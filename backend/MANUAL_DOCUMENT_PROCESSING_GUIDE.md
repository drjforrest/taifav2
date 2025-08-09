# Manual Document Processing Guide
## For TAIFA-FIALA African AI Innovation Platform

### 🎯 **Overview**

This system allows you to drop PDF documents (like your "top 40 African AI startups" report) into a folder and automatically extract structured data using LLM-assisted processing.

**Perfect for:**
- Startup lists and company directories
- Funding announcements and investment reports  
- Market research and analysis reports
- Academic papers with company mentions
- News articles about African AI ecosystem

---

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
# Install new PDF processing dependencies
pip install watchdog pymupdf4llm marker-pdf pymupdftoc
```

### 2. **Setup Database**
```bash
# Add manual documents table to your database
psql your_database < backend/database/schemas/manual_documents.sql
```

### 3. **Start Document Watching Service**
```bash
# Start the folder watcher
python backend/scripts/start_document_watcher.py
```

### 4. **Drop Your PDF + Instructions**
```bash
# Example files in manual_documents/ folder:
manual_documents/
├── top_40_african_ai_startups.pdf
├── top_40_african_ai_startups.txt  # ← Instructions file
└── README.md                       # ← Usage guide
```

---

## 📋 **Document Types Supported**

| Type | Description | Use Case |
|------|------------|----------|
| `startup_list` | Lists of companies/startups | Your top 40 AI startups PDF |
| `funding_announcement` | Funding rounds and investments | Series A/B announcements |
| `market_report` | Market analysis and sizing | Industry research reports |
| `research_paper` | Academic research papers | University research with company mentions |
| `news_article` | News and press releases | Tech news about African AI |
| `pdf_report` | General PDF reports | Miscellaneous documents |

---

## 🔧 **Usage Examples**

### **Example 1: Your Top 40 African AI Startups PDF**

**Files to create:**
```
manual_documents/
├── top_40_african_ai_startups.pdf
└── top_40_african_ai_startups.txt
```

**Instructions file content (`top_40_african_ai_startups.txt`):**
```
TYPE: startup_list
INSTRUCTIONS: Extract company name, description, funding raised, location, domain, and founders from each startup
PROMPT: You are analyzing a comprehensive list of the top 40 African AI startups. For each company mentioned, extract: company name, brief description, total funding raised (if mentioned), headquarters location, AI domain/focus area, and founder names. Return as structured JSON with high confidence scores.
```

### **Example 2: Funding Report**
```
TYPE: funding_announcement
INSTRUCTIONS: Focus on Series A and B rounds, extract investor names and use of funds
PROMPT: Extract funding rounds from this document, focusing on investment amounts, investor details, and how companies plan to use the funding.
```

### **Example 3: Market Research Report**
```
TYPE: market_report
INSTRUCTIONS: Extract market size data, growth rates, and key players
PROMPT: Analyze this market research document and extract market sizing information, growth projections, competitive landscape, and key industry players.
```

---

## 🛠️ **Processing Methods**

### **Method 1: Folder Watching (Recommended)**
```bash
# Start the watcher service
python backend/scripts/start_document_watcher.py

# Drop files in manual_documents/ folder
# Processing happens automatically
# Check completed/ folder for results
```

### **Method 2: API Upload**
```bash
# Start FastAPI server
uvicorn main:app --reload

# Upload via API
curl -X POST "http://localhost:8000/api/manual-documents/upload" \
  -F "file=@top_40_african_ai_startups.pdf" \
  -F "document_type=startup_list" \
  -F "instructions=Extract company details with funding info"
```

### **Method 3: Single Document Test**
```bash
# Test a single document
python backend/scripts/test_document_processor.py \
  top_40_african_ai_startups.pdf \
  --type startup_list \
  --instructions "Focus on funding amounts and locations" \
  --output-file results.json
```

---

## 📊 **Monitoring and Results**

### **API Endpoints**
```bash
# Check processing status
GET /api/manual-documents/status

# Get document details  
GET /api/manual-documents/{document_id}

# Get processing statistics
GET /api/manual-documents/stats/summary

# Reprocess with new instructions
POST /api/manual-documents/{document_id}/reprocess
```

### **Database Queries**
```sql
-- Check processed documents
SELECT file_name, document_type, processing_status, confidence_score 
FROM manual_documents 
ORDER BY created_at DESC;

-- Find innovations from manual documents
SELECT i.title, i.description, i.location, md.file_name
FROM innovations i
JOIN manual_documents md ON i.source_document_id = md.id
WHERE md.document_type = 'startup_list';

-- Get processing statistics
SELECT 
    document_type,
    COUNT(*) as total,
    AVG(confidence_score) as avg_confidence,
    SUM(CASE WHEN processing_status = 'completed' THEN 1 ELSE 0 END) as completed
FROM manual_documents 
GROUP BY document_type;
```

---

## 🎯 **Best Practices**

### **1. Document Type Selection**
- **Startup Lists** → Use `startup_list` type
- **Investment News** → Use `funding_announcement` type  
- **Research Reports** → Use `market_report` type
- **When unsure** → Use `pdf_report` type

### **2. Writing Good Instructions**
```
Good: "Extract company name, funding amount, and location for each startup"
Bad: "Get information about companies"

Good: "Focus on Series A and B funding rounds with specific amounts"
Bad: "Find funding info"
```

### **3. Custom Prompts for Specialized Content**
```
For African-specific content:
"You are an expert on African AI startups. Pay special attention to companies based in Nigeria, Kenya, South Africa, Ghana, and Egypt. Extract local context and market focus."

For technical documents:
"Focus on AI technology domains like computer vision, NLP, machine learning, and robotics. Extract technical specifications where available."
```

### **4. Quality Control**
- **High confidence (>0.8)** → Results likely accurate
- **Medium confidence (0.6-0.8)** → Review results manually
- **Low confidence (<0.6)** → Consider reprocessing with better instructions

---

## 📈 **Expected Results**

### **From Your Top 40 African AI Startups PDF:**
```json
{
  "startups": [
    {
      "name": "Flutterwave",
      "description": "Payment infrastructure for global merchants and payment service providers",
      "funding_raised": "$250 million",
      "location": "Nigeria",
      "domain": "FinTech",
      "founders": ["Olugbenga Agboola", "Iyinoluwa Aboyeji"],
      "website": "flutterwave.com"
    },
    {
      "name": "Andela", 
      "description": "Talent marketplace connecting companies with global technologists",
      "funding_raised": "$200 million",
      "location": "Nigeria",
      "domain": "TalentTech",
      "founders": ["Jeremy Johnson", "Ian Carnevale"]
    }
  ],
  "confidence_score": 0.85
}
```

### **Integration with ETL Pipeline:**
- Extracted innovations flow into main `innovations` table
- Funding information enhances funding data completeness
- Location data improves geographic coverage
- Company details provide rich context for analysis

---

## 🔧 **Troubleshooting**

### **Common Issues:**

**1. PDF Text Extraction Fails**
```
Solution: Install PyMuPDF for better PDF support
pip install pymupdf

Check: PDF might be image-based (scanned) - needs OCR
```

**2. Low Confidence Scores**
```
Solution: Add more specific instructions
Example: Change "Extract companies" to "Extract company names, locations, and funding amounts from the numbered list"
```

**3. No Innovations Extracted**
```
Solution: Wrong document type or poor instructions
- Try different document type
- Add more specific prompt
- Check if PDF contains actual company information
```

**4. LLM API Errors**
```
Check: OpenAI/Anthropic API keys are set
Export OPENAI_API_KEY="your-key"
Export ANTHROPIC_API_KEY="your-key"
```

---

## 💡 **Advanced Usage**

### **Custom Processing Pipeline**
```python
# Process programmatically
from services.manual_document_processor import process_single_document

result = await process_single_document(
    file_path="your_document.pdf",
    document_type="startup_list",
    instructions="Extract only companies with >$1M funding",
    custom_prompt="Focus on well-funded startups with clear business models"
)
```

### **Batch Processing Multiple Documents**
```bash
# Process multiple documents
for pdf in *.pdf; do
    python backend/scripts/test_document_processor.py "$pdf" \
        --type startup_list \
        --output-file "${pdf%.pdf}_results.json"
done
```

### **Integration with Existing ETL**
The extracted data automatically flows into your existing ETL pipeline:
- Innovations → `innovations` table
- Funding info → Enhances funding data completeness
- Market data → Improves market context
- Company details → Enriches company profiles

---

## 🚀 **Next Steps**

1. **Install dependencies** and set up database schema
2. **Test with your top 40 startups PDF** using the test script
3. **Refine instructions** based on initial results
4. **Set up folder watching** for ongoing document processing
5. **Monitor results** through API endpoints
6. **Integrate with dashboard** to view extracted innovations

This system will significantly improve your data completeness and reduce manual data entry for reports like your African AI startups PDF!
