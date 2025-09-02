import json

def test_collect_npi_success(client, mock_npi_response, db_session):
    # Arrange
    test_npi = "1234567890"
    
    # Act
    response = client.get(f"/collect-npi/{test_npi}")
    
    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["npi"] == test_npi
    assert "first_name" in data
    assert "last_name" in data
    assert "taxonomy" in data