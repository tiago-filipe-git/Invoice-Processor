from google.adk.agents import Agent
from invoices.prompt import invoice_extraction_prompt


root_agent = Agent(
    name="Invoice_Agent",
    model="gemini-1.5-flash",
    description="You are an expert document analysis system. Given the pages of a document, answer truthfully and accurately. When answering strictly follow the instructions and post-extraction instructions.",
    instruction=invoice_extraction_prompt,
)
