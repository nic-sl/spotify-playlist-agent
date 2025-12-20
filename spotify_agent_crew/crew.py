from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from typing import List

from spotify_agent_crew.models.SpotifyTrackURIs import SpotifyTrackURIs
from spotify_agent_crew.tools.spotify_api_tools import SpotifyAPITools


def run(request: str = None):
    try:
        SpotifyAgentCrew().crew().kickoff(inputs={"request": request})
    except Exception as e:
        raise RuntimeError(f"An error occurred while running the crew: {e}")


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
    def curator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['curator_agent'],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def track_validator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['track_validator_agent'],  # type: ignore[index]
            verbose=True,
            tools=[SpotifyAPITools.search_songs]
        )

    @agent
    def playlist_publisher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['playlist_publisher_agent'],  # type: ignore[index]
            verbose=True,
            tools=[SpotifyAPITools.create_playlist]
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
            config=self.tasks_config["validate_tracks"],  # type: ignore[index]
            output_json=SpotifyTrackURIs
        )

    @task
    def publish_playlist(self) -> Task:
        return Task(
            config=self.tasks_config["publish_playlist"],  # type: ignore[index]
            context=[self.validate_tracks()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

