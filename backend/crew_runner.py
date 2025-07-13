from crewai import Agent, Task, Crew, LLM, Process
from crewai import BaseLLM
from openai import OpenAI
import os
import weave
from qr_gen_replicate import generate_qr_art
import re
import requests

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

def run_crew(topic: str, qr_data: str = 'behnamshahbazi.com/qrwe'):
    try:
        weave.init(project_name="weavehacks")
        print("✅ Weave initialized successfully")
    except Exception as e:
        print(f"⚠️ Weave initialization failed: {e}")
        print("⚠️ Crew AI will continue without Weave tracing")
    
    wandb_api_key = os.getenv("WANDB_API_KEY")
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

    researcher = Agent(
        role='Research Analyst',
        goal='Find and analyze the best investment opportunities',
        backstory='Expert in financial analysis and market research',
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    qr_generator = Agent(
        role='QR Art Generator',
        goal='Generate artistic QR code images based on research topic',
        backstory='Expert in generative AI art and QR code design',
        tools=[generate_qr_art],
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    writer = Agent(
        role='Report Writer',
        goal='Write clear and concise investment reports',
        backstory='Experienced in creating detailed financial reports',
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description='Deep research on the {topic}',
        expected_output='Comprehensive market data including key players, market size, and growth trends.',
        agent=researcher
    )

    qr_task = Task(
        description='Use the QR code art generation tool to generate an artistic QR code for the research topic. Do not answer in text; only use the tool.',
        expected_output='A PNG image file of the artistic QR code saved to disk or a URL to the generated image.',
        agent=qr_generator
    )

    writing_task = Task(
        description='Write a detailed report based on the research and include the QR code art',
        expected_output='The report should be easy to read and understand. Use bullet points where applicable. Reference the generated QR code art.',
        agent=writer
    )

    crew = Crew(
        agents=[researcher, qr_generator, writer],
        tasks=[research_task, qr_task, writing_task],
        verbose=True,
        process=Process.sequential,
    )

    EXA_API_KEY = os.getenv("EXA_API_KEY", "your_exa_api_key")
    BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY", "your_browserbase_api_key")

    exa_agent = Agent(
        role      = "EXA Search Agent",
        goal      = "Retrieve brand identity URLs via EXA AI",
        backstory = "Specialist in semantic web search with EXA",
        llm       = llm,
        verbose   = True
    )
    scraper_agent = Agent(
        role      = "Browserbase Scraper",
        goal      = "Fetch page text from URLs via Browserbase",
        backstory = "Expert web scraper using Browserbase",
        llm       = llm,
        verbose   = True
    )
    style_agent = Agent(
        role      = "Style Extractor",
        goal      = "Find visual descriptors & colors in text",
        backstory = "Knows design language by heart",
        llm       = llm,
        verbose   = True
    )
    research_agent = Agent(
        role      = "Brand Analyst",
        goal      = "Summarize brand identity narrative",
        backstory = "Discerns brand personality and audience",
        llm       = llm,
        verbose   = True
    )
    prompt_agent = Agent(
        role      = "Prompt Engineer",
        goal      = "Produce a rich QR-code prompt",
        backstory = "Crafts image prompts for DALL·E/Stable Diffusion",
        llm       = llm,
        verbose   = True
    )

    def search_with_exa(inputs):
        print({"exa_query": inputs["brand_name"]})
        resp = requests.post(
            "https://api.exa.ai/search",
            headers={"Authorization": f"Bearer {EXA_API_KEY}"},
            json={"query": f"{inputs['brand_name']} visual identity", "numResults": 3}
        ).json()
        urls = [r["url"] for r in resp.get("results",[])]
        print({"exa_results": urls})
        return urls

    def scrape_with_browserbase(inputs):
        out = []
        for url in inputs:
            print({"scrape_url": url})
            text = requests.post(
                "https://api.browserbase.com/scrape",
                headers={"Authorization": f"Bearer {BROWSERBASE_API_KEY}"},
                json={"url": url}
            ).json().get("text","")[:3000]
            out.append({"url": url, "text": text})
        print({"scraped": out})
        return out

    def extract_style(inputs):
        all_text = " ".join(r["text"] for r in inputs)
        keywords = extract_visual_descriptors(all_text)
        colors   = extract_color_palette(inputs)
        print({"style_keywords": keywords, "color_palette": colors})
        return {"style_keywords": keywords, "color_palette": colors}

    def summarize_brand(inputs):
        prompt = (
            f"Given these style keywords {inputs['style_keywords']} and colors {inputs['color_palette']}, "
            "write a concise narrative summary of the brand’s visual identity."
        )
        return research_agent.llm.call(prompt, temperature=0.3)

    def make_qr_prompt(inputs):
        prompt = (
            f"Create an image-generation prompt for an artistic QR code.\n"
            f"Brand summary: {inputs['summary']}\n"
            f"Include design style, color palette, mood, composition details.\n"
            f"The prompt should be a comma-separated list of up to 5 unique keywords and phrases (no duplicates), no more than 120 characters in total, in the style of AI art prompts.\n"
            f"Follow this example for style: 'surreal concept art of a futuristic house floating on a cloud with waterfall, peaceful and modern, cosy, minimalistic, big windows, natural lighting, sci-fi, lots of details, intricate scene, correct, digital painting, fine tuned, 64k'.\n"
            f"Tailor the keywords to the company or brand name, its logo, and its color palette. Respond ONLY with the short prompt for the QR code generator, nothing else."
        )
        return prompt_agent.llm.call(prompt, temperature=0.7)

    # Run the research pipeline
    urls = search_with_exa({"brand_name": topic})
    scraped = scrape_with_browserbase(urls)
    style = extract_style(scraped)
    summary = summarize_brand(style)
    qr_prompt = make_qr_prompt({"summary": summary})
    concise_prompt = qr_prompt.strip().split('\n')[0]
    print(f"[DEBUG] Researched prompt for QR code generator: {concise_prompt}")

    # 2. QR Code Generation (manual tool call)
    qr_image_url = generate_qr_art.func(concise_prompt, qr_code_content=qr_data)
    print(f"[DEBUG] QR code generated at: {qr_image_url}")

    # 3. Report Writing
    report_prompt = (
        f"Write a detailed report based on the following research topic: {topic}.\n\n"
        f"Include this QR code art: {qr_image_url}\n\n"
        f"The QR code was generated using this prompt: '{concise_prompt}'"
    )
    report_result = writer.llm.call(report_prompt)

    return {
        "urls": urls,
        "scraped": scraped,
        "style": style,
        "summary": summary,
        "concise_prompt": concise_prompt,
        "qr_code_url": qr_image_url,
        "report": report_result
    }
