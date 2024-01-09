Feature: gdk component publish works

  @version(min='1.0.0')
  @change_cwd
  Scenario: publish template zip
    Given we have cli installed
    And we make directory helloworld
    And we run gdk component init -t HelloWorld -l python
    And command was successful
    And we verify gdk project files
    And change component name to com.example.PythonHelloWorld
    And change artifact uri for all platform from com.example.PythonHelloWorld to ${context.last_component}
    And we run gdk component build
    And command was successful
    And we verify component zip build files
    And we verify build artifact named ${context.last_component}.zip
    When we run gdk component publish
    And command was successful

  @version(min='1.1.0')
  @change_cwd
  Scenario: publish template zip with directory name
    Given we have cli installed
    And we run gdk component init -t HelloWorld -l python -n HelloWorld
    And command was successful
    And we change directory to HelloWorld
    And we verify gdk project files
    And change component name to com.example.PythonHelloWorld
    And change artifact uri for all platform from com.example.PythonHelloWorld to ${context.last_component}
    And we run gdk component build
    And command was successful
    And we verify component zip build files
    And we verify build artifact named ${context.last_component}.zip
    When we run gdk component publish
    And command was successful

  @version(min='1.1.0')
  @change_cwd
  Scenario: publish template zip with bucket arg
    Given we have cli installed
    And we run gdk component init -t HelloWorld -l python -n HelloWorld
    And command was successful
    And we change directory to HelloWorld
    And we verify gdk project files
    And change component name to com.example.PythonHelloWorld
    And change artifact uri for all platform from com.example.PythonHelloWorld to ${context.last_component}
    And we get s3 bucket name
    When we run gdk component publish -b <last_s3_bucket>
    And command was successful
    And we verify component zip build files
    And we verify build artifact named ${context.last_component}.zip

  @version(gt='1.1.0')
  @change_cwd
  Scenario: publish template maven multi project with mixed uris
    Given we have cli installed
    And we setup gdk project maven-mixed-uris-publish-test from s3
    And we verify gdk project files
    And change component name to com.example.Multi.MixUris.Maven
    When we quietly run gdk component publish
    And command was successful
    And we verify component build files
