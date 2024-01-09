Feature: gdk component build works

  @version(min='1.0.0')
  @change_cwd
  Scenario: build template zip
    Given we have cli installed
    And we make directory HelloWorld
    And we run gdk component init -t HelloWorld -l python
    And command was successful
    And we verify gdk project files
    And change component name to com.example.PythonHelloWorld
    And change artifact uri for all platform from com.example.PythonHelloWorld to ${context.last_component}
    When we run gdk component build
    Then command was successful
    And we verify component zip build files
    And we verify build artifact named ${context.last_component}.zip

  @version(min='1.0.0')
  @change_cwd
  Scenario: build template zip fail with no artifact
    Given we have cli installed
    And we make directory artifact-not-exists
    And we run gdk component init -t HelloWorld -l python
    And command was successful
    And we verify gdk project files
    And change component name to com.example.PythonHelloWorld
    When we run gdk component build
    Then command was unsuccessful
    And we verify component zip build files
    And command output contains "Could not find"
    And command output contains "com.example.PythonHelloWorld.zip"
    And command output contains "Could not find artifact with URI 's3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/com.example.PythonHelloWorld.zip' on s3 or inside the build folders."

  @version(min='1.1.0')
  @change_cwd
  Scenario: build template zip fail with no artifact with directory name
    Given we have cli installed
    And we run gdk component init -t HelloWorld -l python -n artifact-not-exists
    And command was successful
    And we change directory to artifact-not-exists
    And we verify gdk project files
    And change component name to com.example.PythonHelloWorld
    When we run gdk component build
    Then command was unsuccessful
    And we verify component zip build files
    And command output contains "Could not find artifact with URI 's3://BUCKET_NAME/COMPONENT_NAME/COMPONENT_VERSION/com.example.PythonHelloWorld.zip' on s3 or inside the build folders."

  @version(min='1.1.0')
  @change_cwd
  Scenario: build template maven
    Given we have cli installed
    And we run gdk component init -t HelloWorld -l java -n HelloWorld
    And command was successful
    And we change directory to HelloWorld
    And we verify gdk project files
    And change component name to com.example.JavaHelloWorld
    When we run gdk component build
    Then command was successful
    And we verify component build files

  @version(min='1.1.0')
  @change_cwd
  Scenario: build template maven
    Given we have cli installed
    And we run gdk component init -t HelloWorld -l java -n HelloWorld
    And command was successful
    And we change directory to HelloWorld
    And we verify gdk project files
    And change component name to com.example.JavaHelloWorld
    When we quietly run gdk component build
    Then command was successful
    And we verify component build files

  @version(min='1.1.0')
  @change_cwd
  Scenario: build template gradle multi project
    Given we have cli installed
    And we setup gdk project gradle-build-test from s3
    And we verify gdk project files
    And change component name to com.example.Multi.Gradle
    When we quietly run gdk component build
    Then command was successful
    And we verify component build files

  @version(min='1.1.0')
  @change_cwd
  Scenario: build template maven multi project
    Given we have cli installed
    And we setup gdk project maven-build-test from s3
    And we verify gdk project files
    And change component name to com.example.Multi.Maven
    When we quietly run gdk component build
    Then command was successful
    And we verify component build files


  @version(gt='1.1.0')
  @change_cwd
  Scenario: build gradle kotlin multi project
    Given we have cli installed
    And we setup gdk project gradle-kotlin-build-test from s3
    And we verify gdk project files
    And change component name to com.example.Multi.Gradle.Kotlin
    When we quietly run gdk component build
    Then command was successful
    And we verify component build files

  @version(gt='1.6.1')
  @change_cwd
  Scenario: build gradle kotlin multi project using gradle wrapper
    Given we have cli installed
    And we setup gdk project gradle-kotlin-build-test from s3
    And we verify gdk project files
    And change component name to com.example.Multi.Gradle.Kotlin
    And change build system to gradlew
    And set ./gradlew to executable
    When we quietly run gdk component build
    Then command was successful
    And we verify component build files


  @version(min='1.2.2')
  @change_cwd
  Scenario: build template zip with excludes options
    Given we have cli installed
    And we make directory HelloWorld
    And we run gdk component init -t HelloWorld -l python
    And command was successful
    And we verify gdk project files
    And change component name to com.example.PythonHelloWorld
    And change artifact uri for all platform from com.example.PythonHelloWorld to ${context.last_component}
    And change build options to {"excludes":["main.py"], "zip_name": ""}
    When we run gdk component build
    Then command was successful
    And we verify component zip build files
    And we verify build artifact named ${context.last_component}.zip
    And we verify the following files in ${context.last_component}.zip
      | excluded    | included  |
      | ["main.py"] | ["tests"] |
