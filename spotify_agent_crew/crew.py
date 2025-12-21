"""Crew configuration and entrypoints for the Spotify agent crew.

This module defines the CrewAI-based crew, its agents, and tasks. It also
exposes a small `run()` helper that kicks off the crew with the provided
inputs. Business logic and configuration for agents and tasks are provided via
the CrewAI decorators and external config.
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from spotify_agent_crew.models.tracks_model import TracksModel
from spotify_agent_crew.models.artists_model import ArtistsModel
from spotify_agent_crew.tools.lastfm_api_tools import LastFmAPITools
from spotify_agent_crew.tools.spotify_api_tools import SpotifyAPITools

from typing import List

def run(request: str = None):
    """Kick off the configured crew with a request string.

    Parameters:
        request: Optional textual prompt provided by the user.

    Raises:
        RuntimeError: If the underlying crew execution raises an exception.
    """
    try:
        SpotifyAgentCrew().crew().kickoff(inputs={"request": request})
    except Exception as e:
        raise RuntimeError(f"An error occurred while running the crew: {e}")

# noinspection PyArgumentList
@CrewBase
class SpotifyAgentCrew:
    """Crew container defining agents and tasks for the playlist workflow.

    The agents and tasks are configured using CrewAI's decorators and external
    configuration loaded by the framework (e.g., YAML/pyproject). This class
    provides factories for agents and tasks and a `crew()` method assembling
    them into a runnable process.
    """
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher_agent(self) -> Agent:
        """Create the researcher agent that analyzes the prompt."""
        return Agent(
            config=self.agents_config['researcher_agent'],  # type: ignore[index]
            verbose=True,
            tools=[LastFmAPITools.get_similar_artists]
        )

    @agent
    def track_selector_agent(self) -> Agent:
        """Create the agent that selects tracks using Spotify tools."""
        return Agent(
            config=self.agents_config['track_selector_agent'],  # type: ignore[index]
            verbose=True,
            tools=[SpotifyAPITools.get_tracks]
        )

    @agent
    def playlist_publisher_agent(self) -> Agent:
        """Create the agent that publishes the playlist to Spotify."""
        return Agent(
            config=self.agents_config['playlist_publisher_agent'],  # type: ignore[index]
            verbose=True,
            tools=[SpotifyAPITools.create_playlist]
        )

    @task
    def analyze_prompt(self) -> Task:
        """Define the task that analyzes the user's request into artists."""
        return Task(
            config=self.tasks_config["analyze_prompt"],  # type: ignore[index]
            output_json=ArtistsModel
        )

    @task
    def define_tracks(self) -> Task:
        """Define the task that selects tracks based on chosen artists."""
        return Task(
            config=self.tasks_config["define_tracks"],  # type: ignore[index]
            output_json=TracksModel
        )

    @task
    def publish_playlist(self) -> Task:
        """Define the task that creates the playlist and adds tracks."""
        return Task(
            config=self.tasks_config["publish_playlist"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Assemble and return the runnable crew.

        The crew runs tasks sequentially with verbose logging enabled.
        """
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

