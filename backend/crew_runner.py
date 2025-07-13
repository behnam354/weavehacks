from crewai import Agent, Task, Crew, LLM, Process
from crewai import BaseLLM
from crewai.tools import tool
from openai import OpenAI
import os
import weave
from qr_gen_replicate import generate_qr_art
import re
import requests

# Remove the module-level environment variable loading
# EXA_API_KEY = os.getenv("EXA_API_KEY")
# BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")

# Debug: Print API key status (without exposing the actual keys)
# print(f"EXA_API_KEY loaded: {'Yes' if EXA_API_KEY else 'No'}")
# print(f"BROWSERBASE_API_KEY loaded: {'Yes' if BROWSERBASE_API_KEY else 'No'}")
# if EXA_API_KEY:
#     print(f"EXA_API_KEY length: {len(EXA_API_KEY)}")
#     print(f"EXA_API_KEY starts with: {EXA_API_KEY[:10]}...")
# if BROWSERBASE_API_KEY:
#     print(f"BROWSERBASE_API_KEY length: {len(BROWSERBASE_API_KEY)}")
#     print(f"BROWSERBASE_API_KEY starts with: {BROWSERBASE_API_KEY[:10]}...")

class DummyLLM:
    def call(self, prompt: str, **kwargs):
        # Return a constant string or simulate tool call
        return "CALL_TOOL_QRCodeArtGenerator('dummy prompt')"

def extract_color_palette(results):
    all_colors = []
    for r in results:
        text = (r.get("text","") + " " + r.get("summary","") )
        all_colors += re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', text)
    seen, palette = set(), []
    for c in all_colors:
        cl = c.lower()
        if cl not in seen:
            seen.add(cl)
            palette.append(cl)
    return palette[:8]

def extract_visual_descriptors(content):
    descriptor_keywords = {
        "minimalist":   ["minimal", "clean", "simple", "uncluttered"],
        "modern":       ["modern", "contemporary", "sleek", "cutting-edge"],
        "elegant":      ["elegant", "refined", "sophisticated", "polished"],
        "bold":         ["bold", "strong", "impactful", "striking"],
        "friendly":     ["friendly", "warm", "inviting", "approachable"],
        "professional": ["professional", "business", "corporate", "formal"],
        "innovative":   ["innovative", "creative", "forward-thinking", "fresh"],
        "dynamic":      ["dynamic", "energetic", "vibrant", "lively"],
        "premium":      ["premium", "luxury", "high-end", "exclusive"],
        "playful":      ["playful", "fun", "casual", "relaxed"]
    }
    content = content.lower()
    descriptors = []
    for cat, keys in descriptor_keywords.items():
        if any(k in content for k in keys):
            descriptors.append(cat)
    if any(k in content for k in ["geometric", "angular", "sharp"]):
        descriptors.append("geometric")
    if any(k in content for k in ["organic", "flowing", "curved"]):
        descriptors.append("organic")
    if any(k in content for k in ["gradient", "shadow", "depth"]):
        descriptors.append("dimensional")
    return descriptors[:6]

@tool
def exa_search_tool(brand_name: str) -> str:
    """Search for brand visual identity using EXA API"""
    print({"exa_query": brand_name})
    
    # Log search attempt to W&B
    try:
        import wandb
        if wandb.run is not None:
            wandb.log({
                "tool_called": "exa_search_tool",
                "brand_name": brand_name,
                "timestamp": "start"
            })
    except Exception as e:
        print(f"⚠️ Failed to log search start to W&B: {e}")
    
    # Load environment variables here
    EXA_API_KEY = os.getenv("EXA_API_KEY")
    if not EXA_API_KEY:
        print("⚠️ EXA_API_KEY not found - using fallback URLs")
        fallback_urls = [
            f"https://www.google.com/search?q={brand_name}+visual+identity",
            f"https://www.google.com/search?q={brand_name}+brand+design",
            f"https://www.google.com/search?q={brand_name}+logo+design"
        ]
        print({"exa_results": fallback_urls})
        
        # Log fallback usage to W&B
        try:
            import wandb
            if wandb.run is not None:
                wandb.log({
                    "tool_called": "exa_search_tool",
                    "brand_name": brand_name,
                    "result": "fallback_urls",
                    "urls": fallback_urls,
                    "reason": "EXA_API_KEY_not_found"
                })
        except Exception as e:
            print(f"⚠️ Failed to log fallback to W&B: {e}")
        
        return str(fallback_urls)
    
    try:
        resp = requests.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": EXA_API_KEY},
            json={"query": f"{brand_name} visual identity", "numResults": 3}
        )
        
        print(f"EXA API Status Code: {resp.status_code}")
        print(f"EXA API Response: {resp.text}")
        
        if resp.status_code != 200:
            print(f"❌ EXA API error: {resp.status_code} - using fallback URLs")
            fallback_urls = [
                f"https://www.google.com/search?q={brand_name}+visual+identity",
                f"https://www.google.com/search?q={brand_name}+brand+design",
                f"https://www.google.com/search?q={brand_name}+logo+design"
            ]
            print({"exa_results": fallback_urls})
            
            # Log fallback usage to W&B
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({
                        "tool_called": "exa_search_tool",
                        "brand_name": brand_name,
                        "result": "fallback_urls",
                        "urls": fallback_urls,
                        "reason": "EXA_API_error"
                    })
            except Exception as e:
                print(f"⚠️ Failed to log fallback to W&B: {e}")
            
            return str(fallback_urls)
        
        data = resp.json()
        urls = [r["url"] for r in data.get("results",[])]
        print({"exa_results": urls})
        
        # If no URLs found, use fallback
        if not urls:
            print("⚠️ No EXA results found - using fallback URLs")
            fallback_urls = [
                f"https://www.google.com/search?q={brand_name}+visual+identity",
                f"https://www.google.com/search?q={brand_name}+brand+design",
                f"https://www.google.com/search?q={brand_name}+logo+design"
            ]
            print({"exa_results": fallback_urls})
            
            # Log fallback usage to W&B
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({
                        "tool_called": "exa_search_tool",
                        "brand_name": brand_name,
                        "result": "fallback_urls",
                        "urls": fallback_urls,
                        "reason": "EXA_no_results"
                    })
            except Exception as e:
                print(f"⚠️ Failed to log fallback to W&B: {e}")
            
            return str(fallback_urls)
        
        return str(urls)
        
    except Exception as e:
        print(f"❌ EXA search failed: {e} - using fallback URLs")
        fallback_urls = [
            f"https://www.google.com/search?q={brand_name}+visual+identity",
            f"https://www.google.com/search?q={brand_name}+brand+design",
            f"https://www.google.com/search?q={brand_name}+logo+design"
        ]
        print({"exa_results": fallback_urls})
        
        # Log fallback usage to W&B
        try:
            import wandb
            if wandb.run is not None:
                wandb.log({
                    "tool_called": "exa_search_tool",
                    "brand_name": brand_name,
                    "result": "fallback_urls",
                    "urls": fallback_urls,
                    "reason": "EXA_search_exception"
                })
        except Exception as e:
            print(f"⚠️ Failed to log fallback to W&B: {e}")
        
        return str(fallback_urls)

@tool
def browserbase_scrape_tool(urls: str) -> str:
    """Scrape URLs using Browserbase API"""
    print(f"[DEBUG] browserbase_scrape_tool received: {urls}")
    
    # Load environment variables here
    BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
    
    try:
        url_list = eval(urls) if isinstance(urls, str) else urls
    except:
        print(f"[DEBUG] Failed to eval URLs, treating as single URL")
        url_list = [urls]
    
    print(f"[DEBUG] Processing {len(url_list)} URLs: {url_list}")
    
    out = []
    for url in url_list:
        print({"scrape_url": url})
        
        if not BROWSERBASE_API_KEY:
            print("⚠️ BROWSERBASE_API_KEY not found - using fallback content")
            # Extract brand name from URL for fallback content
            brand_name = url.split('=')[-1].replace('+', ' ') if '=' in url else "the brand"
            fallback_text = f"Information about {brand_name} visual identity and brand design. This brand focuses on modern design principles with a clean aesthetic."
            out.append({"url": url, "text": fallback_text})
            continue
        
        try:
            resp = requests.post(
                "https://api.browserbase.com/scrape",
                headers={"Authorization": f"Bearer {BROWSERBASE_API_KEY}"},
                json={"url": url}
            )
            
            print(f"Browserbase API Status Code for {url}: {resp.status_code}")
            print(f"Browserbase API Response for {url}: {resp.text[:500]}...")
            
            if resp.status_code != 200:
                print(f"❌ Browserbase API error for {url}: {resp.status_code} - using fallback content")
                brand_name = url.split('=')[-1].replace('+', ' ') if '=' in url else "the brand"
                fallback_text = f"Information about {brand_name} visual identity and brand design. This brand focuses on modern design principles with a clean aesthetic."
                out.append({"url": url, "text": fallback_text})
                continue
            
            data = resp.json()
            text = data.get("text","")[:3000]
            
            if not text.strip():
                print(f"⚠️ No text content from {url} - using fallback content")
                brand_name = url.split('=')[-1].replace('+', ' ') if '=' in url else "the brand"
                fallback_text = f"Information about {brand_name} visual identity and brand design. This brand focuses on modern design principles with a clean aesthetic."
                text = fallback_text
            
            out.append({"url": url, "text": text})
            
        except Exception as e:
            print(f"❌ Scraping failed for {url}: {e} - using fallback content")
            brand_name = url.split('=')[-1].replace('+', ' ') if '=' in url else "the brand"
            fallback_text = f"Information about {brand_name} visual identity and brand design. This brand focuses on modern design principles with a clean aesthetic."
            out.append({"url": url, "text": fallback_text})
    
    print({"scraped": out})
    return str(out)

@tool
def style_extraction_tool(scraped_content: str) -> str:
    """Extract style keywords and color palette from scraped content"""
    print(f"[DEBUG] style_extraction_tool received: {scraped_content[:200]}...")
    
    try:
        content_list = eval(scraped_content) if isinstance(scraped_content, str) else scraped_content
    except:
        print(f"[DEBUG] Failed to eval scraped_content, treating as single text")
        content_list = [{"text": scraped_content}]
    
    print(f"[DEBUG] Processing {len(content_list)} content items")
    
    all_text = " ".join(r.get("text", "") for r in content_list)
    keywords = extract_visual_descriptors(all_text)
    colors = extract_color_palette(content_list)
    
    # Fallback defaults
    if not keywords:
        keywords = ["modern", "professional", "clean"]
    if not colors:
        colors = ["#000000", "#ffffff", "#007acc", "#f0f0f0"]
    
    result = {"style_keywords": keywords, "color_palette": colors}
    print({"style_keywords": keywords, "color_palette": colors})
    return str(result)

@tool
def generate_qr_art_tool(prompt: str, qr_code_content: str) -> str:
    """Generate artistic QR code using the provided prompt and QR data"""
    print(f"[DEBUG] generate_qr_art_tool called with prompt: {prompt[:100]}...")
    print(f"[DEBUG] generate_qr_art_tool called with qr_code_content: {qr_code_content}")
    
    # Log QR generation attempt to W&B
    try:
        import wandb
        if wandb.run is not None:
            wandb.log({
                "tool_called": "generate_qr_art_tool",
                "prompt_length": len(prompt),
                "qr_code_content": qr_code_content,
                "timestamp": "start"
            })
    except Exception as e:
        print(f"⚠️ Failed to log QR generation start to W&B: {e}")
    
    try:
        result = generate_qr_art.func(prompt, qr_code_content=qr_code_content)
        print(f"[DEBUG] generate_qr_art_tool result: {result}")
        
        # Log successful QR generation to W&B
        try:
            import wandb
            if wandb.run is not None:
                wandb.log({
                    "tool_called": "generate_qr_art_tool",
                    "result": "success",
                    "qr_url": result,
                    "prompt_length": len(prompt)
                })
        except Exception as e:
            print(f"⚠️ Failed to log QR success to W&B: {e}")
        
        return result
    except Exception as e:
        print(f"❌ generate_qr_art_tool failed: {e}")
        
        # Log QR generation failure to W&B
        try:
            import wandb
            if wandb.run is not None:
                wandb.log({
                    "tool_called": "generate_qr_art_tool",
                    "result": "failure",
                    "error": str(e),
                    "prompt_length": len(prompt)
                })
        except Exception as we:
            print(f"⚠️ Failed to log QR failure to W&B: {we}")
        
        return f"QR generation failed: {e}"

@tool
def generate_qr_art_fallback(brand_name: str, qr_data: str) -> str:
    """Generate a simple artistic QR code using just the brand name when detailed information isn't available"""
    print(f"[DEBUG] Using fallback QR generation for brand: {brand_name}")
    
    # Create a simple but effective prompt using just the brand name
    fallback_prompt = f"""
    Create an artistic QR code for {brand_name}.
    Design a modern, professional QR code that represents the brand.
    Use a clean, minimalist design with subtle artistic elements.
    Ensure the QR code remains scannable while incorporating the brand name visually.
    Use a professional color scheme with good contrast.
    """
    
    print(f"[DEBUG] Fallback prompt: {fallback_prompt}")
    
    try:
        result = generate_qr_art.func(fallback_prompt, qr_code_content=qr_data)
        print(f"[DEBUG] Fallback QR code generated: {result}")
        return result
    except Exception as e:
        print(f"❌ Fallback QR generation failed: {e}")
        return "QR generation failed"

def run_crew(topic: str, qr_data: str = 'behnamshahbazi.com/qrwe'):
    try:
        import wandb
        if wandb.run is None:
            wandb.init(project="weavehacks")
        print("✅ W&B initialized successfully")
    except Exception as e:
        print(f"⚠️ W&B initialization failed: {e}")
        print("⚠️ Crew AI will continue without W&B tracing")
    
    # Debug: Check environment variables
    EXA_API_KEY = os.getenv("EXA_API_KEY")
    BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
    WANDB_API_KEY = os.getenv("WANDB_API_KEY")
    
    print(f"[DEBUG] Environment variables check:")
    print(f"[DEBUG] EXA_API_KEY loaded: {'Yes' if EXA_API_KEY else 'No'}")
    print(f"[DEBUG] BROWSERBASE_API_KEY loaded: {'Yes' if BROWSERBASE_API_KEY else 'No'}")
    print(f"[DEBUG] WANDB_API_KEY loaded: {'Yes' if WANDB_API_KEY else 'No'}")
    
    if EXA_API_KEY:
        print(f"[DEBUG] EXA_API_KEY length: {len(EXA_API_KEY)}")
        print(f"[DEBUG] EXA_API_KEY starts with: {EXA_API_KEY[:10]}...")
    if BROWSERBASE_API_KEY:
        print(f"[DEBUG] BROWSERBASE_API_KEY length: {len(BROWSERBASE_API_KEY)}")
        print(f"[DEBUG] BROWSERBASE_API_KEY starts with: {BROWSERBASE_API_KEY[:10]}...")
    
    wandb_api_key = WANDB_API_KEY
    if not wandb_api_key:
        print("⚠️ WANDB_API_KEY not found - Crew AI will use fallback LLM")
        # You could add a fallback LLM here if needed
        return "Crew AI workflow completed (W&B not configured)"

    class WandbOpenAILLM(BaseLLM):
        def __init__(self, model, api_key, base_url, project):
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key,
                project=project
            )
            self.model = model

        def call(self, prompt: str, **kwargs) -> str:
            try:
                if isinstance(prompt, list):
                    prompt_str = ""
                    for msg in prompt:
                        role = msg.get("role", "user").capitalize()
                        content = msg.get("content", "")
                        prompt_str += f"{role}: {content}\n"
                else:
                    prompt_str = prompt

                formatted_prompt = f"### Instruction:\n{prompt_str.strip()}\n\n### Response:\n"

                response = self.client.completions.create(
                    model=self.model,
                    prompt=formatted_prompt,
                    max_tokens=512,
                    temperature=0.7
                )

                return response.choices[0].text.strip()
            except Exception as e:
                print("❌ [ERROR] Wandb LLM call failed:", e)
                raise

    llm = WandbOpenAILLM(
        model="microsoft/Phi-4-mini-instruct",
        api_key=wandb_api_key,
        base_url="https://api.inference.wandb.ai/v1",
        project="behnam-shahbazi40-dropbox/weavehacks"
    )

    # --- Define modular pipeline agents with tools ---
    exa_agent = Agent(
        role='EXA Search Agent',
        goal='Find URLs about the brand\'s visual identity using EXA',
        backstory='Specialist in semantic web search with EXA',
        tools=[exa_search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    scraper_agent = Agent(
        role='Browserbase Scraper Agent',
        goal='Scrape URLs for text content using Browserbase',
        backstory='Expert in web scraping and content extraction',
        tools=[browserbase_scrape_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    style_agent = Agent(
        role='Style Extractor Agent',
        goal='Extract style keywords and color palette from content',
        backstory='Expert in visual analysis and style extraction',
        tools=[style_extraction_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research_agent = Agent(
        role='Brand Analyst Agent',
        goal='Summarize the brand’s visual identity',
        backstory='Expert in brand analysis and summarization',
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    prompt_agent = Agent(
        role='Prompt Engineer Agent',
        goal='Craft a high-quality AI art prompt for QR code generation',
        backstory='Expert in prompt engineering for generative AI',
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    qr_generator_agent = Agent(
        role='QR Code Generator Agent',
        goal='Generate artistic QR code images by calling the appropriate tools (generate_qr_art_tool or generate_qr_art_fallback) and return the URL',
        backstory='Expert in generative AI art and QR code design. Always uses tools to generate QR codes and returns the actual URL, never just describes what would be done.',
        tools=[generate_qr_art_tool, generate_qr_art_fallback],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # --- Create Tasks for each Agent ---
    search_task = Task(
        description=f"""
        Search for information about {topic}'s visual identity and brand design.
        Use the exa_search_tool with the brand name '{topic}' to find relevant URLs about the brand's visual identity, 
        design language, color palette, and overall aesthetic.
        Focus on finding official brand websites, design articles, and visual identity guides.
        
        Brand to research: {topic}
        
        IMPORTANT: Make sure to call the exa_search_tool function with the brand name '{topic}'.
        """,
        agent=exa_agent,
        expected_output="A list of relevant URLs about the brand's visual identity"
    )

    scrape_task = Task(
        description="""
        Scrape the provided URLs to extract text content about the brand's visual identity.
        
        IMPORTANT: Use the URLs from the previous search task. The search task provided a list of URLs that you need to scrape.
        Use the browserbase_scrape_tool with those URLs to scrape each URL and extract meaningful text content.
        Focus on content that describes the brand's design, colors, typography, and visual elements.
        
        The URLs should be passed as a string to the browserbase_scrape_tool function.
        """,
        agent=scraper_agent,
        expected_output="Scraped text content from the URLs with focus on visual identity information",
        context=[search_task]
    )

    style_extraction_task = Task(
        description="""
        Analyze the scraped content to extract style keywords and color palette information.
        
        IMPORTANT: Use the scraped content from the previous scraping task. The scraping task provided text content from various URLs.
        Use the style_extraction_tool with that scraped content to identify visual descriptors, design styles, and color schemes.
        
        The scraped content should be passed as a string to the style_extraction_tool function.
        """,
        agent=style_agent,
        expected_output="A dictionary containing style_keywords and color_palette arrays",
        context=[scrape_task]
    )

    brand_analysis_task = Task(
        description=f"""
        Create a comprehensive summary of the brand's visual identity based on the extracted style information.
        
        IMPORTANT: You have access to the style analysis from the previous task. The style extraction task provided:
        - Style keywords (like "modern", "professional", "clean", etc.)
        - Color palette (like "#000000", "#ffffff", etc.)
        
        Use this information to write a concise narrative about the brand's visual identity.
        Do NOT ask for URLs or additional information - use what you have from the previous task.
        
        Brand being analyzed: {topic}
        
        Write a 2-3 sentence summary of the brand's visual personality based on the style keywords and colors.
        """,
        agent=research_agent,
        expected_output="A 2-3 sentence summary of the brand's visual identity based on style keywords and colors",
        context=[style_extraction_task]
    )

    prompt_creation_task = Task(
        description=f"""
        Create a high-quality AI art prompt for generating an artistic QR code for {topic}.
        
        IMPORTANT: You have access to the brand analysis from the previous task. Use that analysis to create a detailed prompt.
        Do NOT ask for URLs or additional information - use what you have from the previous task.
        
        Your prompt should capture:
        - The brand's visual style and aesthetic
        - Color palette and mood
        - Design elements and composition
        - Overall brand personality
        
        FALLBACK: If the brand analysis is empty or generic, create a simple but effective prompt using just the brand name '{topic}'.
        Focus on creating a modern, professional design that represents the brand.
        
        Brand: {topic}
        QR Code Data: {qr_data}
        
        Create a detailed prompt (2-3 sentences) that can be used to generate an artistic QR code.
        """,
        agent=prompt_agent,
        expected_output="A detailed AI art prompt (2-3 sentences) for QR code generation",
        context=[brand_analysis_task]
    )

    qr_generation_task = Task(
        description=f"""
        Generate an artistic QR code using the provided prompt and QR data.
        
        CRITICAL: You MUST call one of the available tools to generate the QR code. Do not just describe what you would do.
        
        You have two tools available:
        1. generate_qr_art_tool - Use this if you have a detailed prompt from the previous task
        2. generate_qr_art_fallback - Use this if the previous task didn't provide good information
        
        STEPS TO FOLLOW:
        1. Check if you received a detailed prompt from the previous prompt creation task
        2. If you have a good prompt, call generate_qr_art_tool with the prompt and QR data '{qr_data}'
        3. If you don't have a good prompt or it's generic, call generate_qr_art_fallback with brand name '{topic}' and QR data '{qr_data}'
        4. Return the URL that the tool provides
        
        IMPORTANT: You MUST call one of these tools. Do not just write a description or ask for more information.
        The tools will return a URL to the generated QR code image.
        
        QR Code Data: {qr_data}
        Brand Name: {topic}
        
        Example tool calls:
        - generate_qr_art_tool("detailed prompt here", "{qr_data}")
        - generate_qr_art_fallback("{topic}", "{qr_data}")
        
        DO NOT ask for URLs or additional information - use what you have and call the tools.
        DO NOT describe what you would do - actually call the tools and return the result.
        """,
        agent=qr_generator_agent,
        expected_output="A URL to the generated artistic QR code image (must be returned by calling a tool)",
        context=[prompt_creation_task]
    )

    # --- Create and run the Crew ---
    crew = Crew(
        agents=[exa_agent, scraper_agent, style_agent, research_agent, prompt_agent, qr_generator_agent],
        tasks=[search_task, scrape_task, style_extraction_task, brand_analysis_task, prompt_creation_task, qr_generation_task],
        process=Process.sequential,
        verbose=True
    )

    # Run the crew
    result = crew.kickoff()

    print(f"[DEBUG] Crew execution completed")
    print(f"[DEBUG] Final result: {result}")
    print(f"[DEBUG] Result type: {type(result)}")
    print(f"[DEBUG] Result has __dict__: {hasattr(result, '__dict__')}")
    if hasattr(result, '__dict__'):
        print(f"[DEBUG] Result __dict__: {result.__dict__}")
    
    # Convert CrewOutput to string if needed for logging
    result_for_logging = str(result) if hasattr(result, '__dict__') else result
    
    # Log the final result to W&B
    try:
        import wandb
        if wandb.run is not None:
            wandb.log({
                "crew_execution_completed": True,
                "topic": topic,
                "qr_data": qr_data,
                "final_result": result_for_logging,
                "result_type": type(result).__name__
            })
            print("✅ Result logged to W&B")
    except Exception as e:
        print(f"⚠️ Failed to log to W&B: {e}")
    
    # Check if the result is a valid QR code URL or if we need to use fallback
    if (isinstance(result, str) and result.startswith('http') and 
        ('replicate.delivery' in result or '.png' in result or '.jpg' in result)):
        print(f"[DEBUG] Valid QR code URL found: {result}")
        # Log successful QR generation to W&B
        try:
            import wandb
            if wandb.run is not None:
                wandb.log({
                    "qr_generation_success": True,
                    "qr_url": result,
                    "method": "crew_generated"
                })
        except Exception as e:
            print(f"⚠️ Failed to log QR success to W&B: {e}")
        return result
    elif isinstance(result, str) and result.startswith('http'):
        # Additional check for any HTTP URL that might be valid
        print(f"[DEBUG] HTTP URL found, assuming valid QR code: {result}")
        # Log successful QR generation to W&B
        try:
            import wandb
            if wandb.run is not None:
                wandb.log({
                    "qr_generation_success": True,
                    "qr_url": result,
                    "method": "crew_generated_http"
                })
        except Exception as e:
            print(f"⚠️ Failed to log QR success to W&B: {e}")
        return result
    elif "URL to the generated" in str(result) or "will be displayed" in str(result) or "please provide" in str(result) or "Awaiting" in str(result):
        print("⚠️ Crew returned placeholder or request for more info - using fallback QR generation")
        try:
            fallback_prompt = f"""
            Create an artistic QR code for {topic}.
            Design a modern, professional QR code that represents the brand.
            Use a clean, minimalist design with subtle artistic elements.
            Ensure the QR code remains scannable while incorporating the brand name visually.
            Use a professional color scheme with good contrast.
            """
            
            fallback_result = generate_qr_art.func(fallback_prompt, qr_code_content=qr_data)
            print(f"[DEBUG] Direct fallback result: {fallback_result}")
            # Log fallback QR generation to W&B
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({
                        "qr_generation_success": True,
                        "qr_url": fallback_result,
                        "method": "fallback_direct"
                    })
            except Exception as e:
                print(f"⚠️ Failed to log fallback success to W&B: {e}")
            return fallback_result
        except Exception as e:
            print(f"❌ Direct fallback also failed: {e}")
            # Log fallback failure to W&B
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({
                        "qr_generation_success": False,
                        "error": str(e),
                        "method": "fallback_direct"
                    })
            except Exception as we:
                print(f"⚠️ Failed to log fallback failure to W&B: {we}")
            return "QR generation failed"
    else:
        print(f"⚠️ Crew result doesn't look like a QR URL: {result}")
        print("⚠️ Using fallback QR generation")
        try:
            # Fix: Call the function directly instead of trying to call the tool object
            fallback_prompt = f"""
            Create an artistic QR code for {topic}.
            Design a modern, professional QR code that represents the brand.
            Use a clean, minimalist design with subtle artistic elements.
            Ensure the QR code remains scannable while incorporating the brand name visually.
            Use a professional color scheme with good contrast.
            """
            
            fallback_result = generate_qr_art.func(fallback_prompt, qr_code_content=qr_data)
            print(f"[DEBUG] Fallback result: {fallback_result}")
            # Log fallback QR generation to W&B
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({
                        "qr_generation_success": True,
                        "qr_url": fallback_result,
                        "method": "fallback_final"
                    })
            except Exception as e:
                print(f"⚠️ Failed to log fallback success to W&B: {e}")
            return fallback_result
        except Exception as e:
            print(f"❌ Fallback failed: {e}")
            # Log final failure to W&B
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({
                        "qr_generation_success": False,
                        "error": str(e),
                        "method": "fallback_final"
                    })
            except Exception as we:
                print(f"⚠️ Failed to log final failure to W&B: {we}")
            return "QR generation failed"
