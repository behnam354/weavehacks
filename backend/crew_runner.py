from crewai import Agent, Task, Crew, LLM, Process
from crewai import BaseLLM
from openai import OpenAI
import os
import weave
from qr_gen_replicate import generate_qr_art

class DummyLLM:
    def call(self, prompt: str, **kwargs):
        # Return a constant string or simulate tool call
        return "CALL_TOOL_QRCodeArtGenerator('dummy prompt')"

def run_crew(topic: str):
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

    # 1. Research
    research_result = researcher.llm.call(
        f"Deep research on the {topic}. Then, in one short sentence, provide a concise, creative prompt for an AI art generator to make a QR code about this topic. Respond ONLY with the short prompt for the QR code generator, nothing else. The prompt should be a comma-separated list of up to 5 unique keywords and phrases (no duplicates), no more than 120 characters in total, in the style of AI art prompts (e.g., 'surreal, futuristic, floating house, cloud, waterfall'). Tailor the keywords to the company or brand name, its logo, and its color palette."
    )

    concise_prompt = research_result.strip().split('\n')[0]  # Use only the first line if multiple
    print(f"[DEBUG] Concise prompt for QR code generator: {concise_prompt}")

    # 2. QR Code Generation (manual tool call)
    qr_image_url = generate_qr_art.func(concise_prompt)
    print(f"[DEBUG] QR code generated at: {qr_image_url}")

    # 3. Report Writing
    report_prompt = (
        f"Write a detailed report based on the following research topic: {topic}.\n\n"
        f"Include this QR code art: {qr_image_url}\n\n"
        f"The QR code was generated using this prompt: '{concise_prompt}'"
    )
    report_result = writer.llm.call(report_prompt)

    return {
        "research": research_result,
        "concise_prompt": concise_prompt,
        "qr_code_url": qr_image_url,
        "report": report_result
    }
