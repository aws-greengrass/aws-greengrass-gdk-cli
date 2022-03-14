Feature: gdk component init works

  @version(min='1.0.0')
  Scenario: init template with non empty dir
    Given we have cli installed
    When we run gdk component init -t HelloWorld -l python
    Then command was unsuccessful
    And command output contains "Try `gdk component init --help`"

  @version(min='1.0.0')
  @change_cwd
  Scenario: init template with empty dir
    Given we have cli installed
    When we run gdk component init -t HelloWorld -l python
    Then command was successful
    And we verify gdk project files

  @version(min='1.1.0')
  @change_cwd
  Scenario: init template with new dir
    Given we have cli installed
    When we run gdk component init -t HelloWorld -l python -n test-dir
    Then command was successful
    And we change directory to test-dir
    And we verify gdk project files

  @version(min='1.0.0')
  @change_cwd
  Scenario: init repository
    Given we have cli installed
    When we run gdk component init -r aws-greengrass-labs-database-influxdb
    Then command was successful
    And we verify gdk project files

  @version(min='1.1.0')
  @change_cwd
  Scenario: init repository with new dir
    Given we have cli installed
    When we run gdk component init -r aws-greengrass-labs-database-influxdb -n test-dir
    Then command was successful
    And we change directory to test-dir
    And we verify gdk project files

  @version(min='1.0.0')
  @change_cwd
  Scenario: init repository not exists
    Given we have cli installed
    When we run gdk component init -r repo-not-exists
    Then command was unsuccessful
    And command output contains "Could not find the component repository 'repo-not-exists' in Greengrass Software Catalog."

  @version(min='1.0.0')
  @change_cwd
  Scenario: init template not exists
    Given we have cli installed
    When we run gdk component init
    Then command was unsuccessful
    And command output contains "Could not initialize the project as the arguments passed are invalid."

