from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from spotify_agent_crew.models.spotify_tracks_model import SpotifyTracksModel
from spotify_agent_crew.models.spotify_artists_model import SpotifyArtistsModel
from spotify_agent_crew.tools.spotify_api_tools import SpotifyAPITools

from typing import List

def run(request: str = None):
    try:
        SpotifyAgentCrew().crew().kickoff(inputs={"request": request})
    except Exception as e:
        raise RuntimeError(f"An error occurred while running the crew: {e}")


# noinspection PyArgumentList
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
    def track_selector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['track_selector_agent'],  # type: ignore[index]
            verbose=True,
            tools=[SpotifyAPITools.get_tracks]
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
            config=self.tasks_config["analyze_prompt"],  # type: ignore[index]
            output_json=SpotifyArtistsModel
        )

    @task
    def define_tracks(self) -> Task:
        return Task(
            config=self.tasks_config["define_tracks"],  # type: ignore[index]
            output_json=SpotifyTracksModel
        )

    @task
    def publish_playlist(self) -> Task:
        return Task(
            config=self.tasks_config["publish_playlist"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

