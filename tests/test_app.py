import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from fastapi import status
from src.app import app, activities

@pytest.mark.asyncio
async def test_root_redirect():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_307_TEMPORARY_REDIRECT)

@pytest.mark.asyncio
async def test_duplicate_signup_validation():
    """Test that the endpoint rejects duplicate sign-ups"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Reset the activity state for testing
        activities["Soccer Team"]["participants"] = ["alex@mergington.edu"]
        
        # Attempt to sign up a student who is already registered
        response = await ac.post(
            "/activities/Soccer%20Team/signup?email=alex@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student already signed up for this activity"

@pytest.mark.asyncio
async def test_unregister_success():
    """Test successful unregistration of a participant"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Setup: ensure the student is registered
        activities["Soccer Team"]["participants"] = ["alex@mergington.edu", "test@mergington.edu"]
        
        # Unregister the student
        response = await ac.post(
            "/activities/Soccer%20Team/unregister?email=test@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Unregistered test@mergington.edu from Soccer Team"
        assert "test@mergington.edu" not in activities["Soccer Team"]["participants"]

@pytest.mark.asyncio
async def test_unregister_non_participant():
    """Test that unregistering a non-participant returns an error"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Reset the activity state
        activities["Soccer Team"]["participants"] = ["alex@mergington.edu"]
        
        # Attempt to unregister someone who is not registered
        response = await ac.post(
            "/activities/Soccer%20Team/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student is not registered for this activity"

@pytest.mark.asyncio
async def test_unregister_nonexistent_activity():
    """Test that unregistering from a non-existent activity returns 404"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"

@pytest.mark.asyncio
async def test_signup_capacity_validation():
    """Test that the endpoint rejects sign-ups when activity is at capacity"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Setup: fill the activity to capacity
        activities["Chess Club"]["max_participants"] = 2
        activities["Chess Club"]["participants"] = ["student1@mergington.edu", "student2@mergington.edu"]
        
        # Attempt to sign up when activity is full
        response = await ac.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Activity is full"
        
        # Cleanup
        activities["Chess Club"]["max_participants"] = 12
        activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]

