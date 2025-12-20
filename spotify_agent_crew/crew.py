from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from typing import List

from spotify_agent_crew.tools.spotify_api_tools import SpotifyAPITools


def run(request: str = None):
    try:
        SpotifyAgentCrew().crew().kickoff(inputs={"request": request})
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


@CrewBase
class SpotifyAgentCrew:
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher_agent'],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def connector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['connector_agent'],  # type: ignore[index]
            verbose=True,
            tools=[SpotifyAPITools.search_songs, SpotifyAPITools.create_playlist]
        )

    @agent
    def curator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['curator_agent'],  # type: ignore[index]
            verbose=True
        )

    @task
    def analyze_prompt(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_prompt"]  # type: ignore[index]
        )

    @task
    def curate_playlist(self) -> Task:
        return Task(
            config=self.tasks_config["curate_playlist"]  # type: ignore[index]
        )

    @task
    def validate_tracks(self) -> Task:
        return Task(
            config=self.tasks_config["validate_tracks"]  # type: ignore[index]
        )

    @task
    def publish_playlist(self) -> Task:
        return Task(
            config=self.tasks_config["publish_playlist"]  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

