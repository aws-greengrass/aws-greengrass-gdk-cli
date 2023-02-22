Feature: gdk component list works

  @version(le='1.1.0')
  Scenario: list component templates
    Given we have cli installed
    When we run gdk component list --template
    Then command was successful
    And command output contains "HelloWorld-python"
    And command output contains "HelloWorld-java"

  @version(min='1.2.0')
  Scenario: list component templates
    Given we have cli installed
    When we run gdk component list --template
    Then command was successful
    And command output contains "HelloWorld (python)"
    And command output contains "HelloWorld (java)"

  @version(min='1.0.0')
  Scenario: list component repository
    Given we have cli installed
    When we run gdk component list --repository
    Then command was successful
    And command output contains "aws-greengrass-labs-database-influxdb"
