# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# mypy: disable-error-code="no-untyped-call"

import uuid
from multiprocessing import Pool
from typing import List
from unittest import TestCase

import pytest
from google.cloud.datastore import Client
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from langchain_google_datastore import DatastoreChatMessageHistory


@pytest.fixture
def test_case() -> TestCase:
    return TestCase()


def test_firestore_history_workflow(test_case: TestCase) -> None:
    session_id = uuid.uuid4().hex
    chat_history = DatastoreChatMessageHistory(
        session_id=session_id, kind="HistoryWorkflow"
    )

    chat_history.add_ai_message("AI message")
    chat_history.add_user_message("User message")

    expected_messages = [
        AIMessage(content="AI message"),
        HumanMessage(content="User message"),
    ]

    test_case.assertCountEqual(expected_messages, chat_history.messages)

    chat_history.clear()
    chat_history._load_messages()

    assert len(chat_history.messages) == 0


def test_firestore_large_history_workflow(test_case: TestCase) -> None:
    session_id = uuid.uuid4().hex
    chat_history = DatastoreChatMessageHistory(
        session_id=session_id, kind="HistoryWorkflow"
    )

    ai_message = "A" * 5000
    user_message = "B" * 5000

    chat_history.add_ai_message(ai_message)
    chat_history.add_user_message(user_message)

    expected_messages = [
        AIMessage(content=ai_message),
        HumanMessage(content=user_message),
    ]

    test_case.assertCountEqual(expected_messages, chat_history.messages)

    chat_history.clear()
    chat_history._load_messages()

    assert len(chat_history.messages) == 0


def test_firestore_load_messages(test_case: TestCase) -> None:
    NUM_MESSAGES = 25
    session_id = uuid.uuid4().hex
    chat_history = DatastoreChatMessageHistory(
        session_id=session_id, kind="HistoryLoad"
    )

    expected_messages: List[BaseMessage] = []

    for i in range(NUM_MESSAGES):
        ai_m = AIMessage(content=f"AI message: {i}")
        human_m = HumanMessage(content=f"Human message: {i}")

        expected_messages.append(ai_m)
        expected_messages.append(human_m)

        chat_history.add_ai_message(ai_m)
        chat_history.add_user_message(human_m)

    test_case.assertCountEqual(expected_messages, chat_history.messages)

    chat_history.clear()
    chat_history._load_messages()

    assert len(chat_history.messages) == 0


def test_firestore_multiple_sessions(test_case: TestCase) -> None:
    kind = "MultipleSession"
    session_1 = uuid.uuid4().hex
    chat_history_1 = DatastoreChatMessageHistory(session_id=session_1, kind=kind)
    session_2 = uuid.uuid4().hex
    chat_history_2 = DatastoreChatMessageHistory(session_id=session_2, kind=kind)

    chat_history_1.add_ai_message("AI message session 1")
    chat_history_1.add_user_message("Human message session 1")
    chat_history_2.add_ai_message("AI message session 2")
    chat_history_2.add_user_message("Human message session 2")

    expected_message_session_1 = [
        AIMessage(content="AI message session 1"),
        HumanMessage(content="Human message session 1"),
    ]
    expected_message_session_2 = [
        AIMessage(content="AI message session 2"),
        HumanMessage(content="Human message session 2"),
    ]

    test_case.assertCountEqual(expected_message_session_1, chat_history_1.messages)
    test_case.assertCountEqual(expected_message_session_2, chat_history_2.messages)

    chat_history_1.clear()
    chat_history_2.clear()

    assert len(chat_history_1.messages) == 0
    assert len(chat_history_2.messages) == 0


def test_firestore_reopen_session(test_case: TestCase) -> None:
    kind = "Session"
    session = uuid.uuid4().hex
    chat_history = DatastoreChatMessageHistory(session_id=session, kind=kind)

    chat_history.add_ai_message("AI message")
    chat_history.add_user_message("Human message")

    chat_history_reopen = DatastoreChatMessageHistory(session_id=session, kind=kind)

    expected_messages = [
        AIMessage(content="AI message"),
        HumanMessage(content="Human message"),
    ]

    test_case.assertCountEqual(expected_messages, chat_history_reopen.messages)

    chat_history.clear()
    chat_history_reopen.clear()


def test_firestore_custom_client(test_case: TestCase) -> None:
    client = Client(namespace="namespace")
    session_id = uuid.uuid4().hex
    chat_history = DatastoreChatMessageHistory(
        session_id=session_id, kind="Custom", client=client
    )

    chat_history.add_ai_message("AI message")
    chat_history.add_user_message("User message")

    expected_messages = [
        AIMessage(content="AI message"),
        HumanMessage(content="User message"),
    ]

    test_case.assertCountEqual(expected_messages, chat_history.messages)

    chat_history.clear()
