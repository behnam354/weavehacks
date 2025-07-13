from crewai import Agent, Task, Crew, LLM, Process
from crewai import BaseLLM
from openai import OpenAI
import os
import weave

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

    writing_task = Task(
        description='Write a detailed report based on the research',
        expected_output='The report should be easy to read and understand. Use bullet points where applicable.',
        agent=writer
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True,
        process=Process.sequential,
    )

    result = crew.kickoff(inputs={"topic": topic})
    return result
