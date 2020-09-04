Feature: Login Git Respository uging oauth

  Scenario: Author start git pull
    When Author enter git pull

    Then Author Login Git lab using oauth

  Scenario: Author Login Git lab using oauth
    When Author Login Git lab using oauth
    Then Author create an application by posting a JSON payload