import pytest

from django_broadcaster.events import CloudEvent


def test_cloud_event_initialization():
    """Test that a CloudEvent can be initialized with the correct attributes"""
    event = CloudEvent(
        event_type="test.event",
        source="test-source",
        subject="test-subject",
        data={"test": "data"},
        data_content_type="application/json",
        data_schema="https://example.com/schema",
        spec_version="1.0",
    )

    assert event.event_type == "test.event"
    assert event.source == "test-source"
    assert event.subject == "test-subject"
    assert event.data == {"test": "data"}
    assert event.data_content_type == "application/json"
    assert event.data_schema == "https://example.com/schema"
    assert event.spec_version == "1.0"


def test_cloud_event_to_dict():
    """Test that a CloudEvent can be converted to a dictionary"""
    event = CloudEvent(
        event_type="test.event",
        source="test-source",
        subject="test-subject",
        data={"test": "data"},
    )

    event_dict = event.to_dict()

    assert event_dict["specversion"] == "1.0"
    assert event_dict["type"] == "test.event"
    assert event_dict["source"] == "test-source"
    assert event_dict["subject"] == "test-subject"
    assert event_dict["datacontenttype"] == "application/json"
    assert event_dict["data"] == {"test": "data"}


def test_cloud_event_to_dict_optional_fields():
    """Test that a CloudEvent can be converted to a dictionary with optional fields"""
    event = CloudEvent(event_type="test.event", source="test-source")

    event_dict = event.to_dict()

    assert "subject" not in event_dict
    assert "dataschema" not in event_dict
    assert "data" not in event_dict


def test_cloud_event_fixture(cloud_event):
    """Test that the cloud_event fixture works correctly"""
    assert cloud_event.event_type == "test.event"
    assert cloud_event.source == "test-source"
    assert cloud_event.subject == "test-subject"
    assert cloud_event.data == {"test": "data"}
