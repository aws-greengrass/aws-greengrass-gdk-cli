Feature: As a component builder, I can run `gdk test-e2e build` command to build the testing module using GDK config and command arguments.

    @version(min='1.3.0')
    @change_cwd
    Scenario: test-e2e-build-1: As a component builder, when I run the test-e2e build command, test feature files are updated and then the module is built.
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n HelloWorld
        Then command was successful
        And we change directory to HelloWorld
        And change component name to com.example.PythonHelloWorld
        And change artifact uri for all platform from com.example.PythonHelloWorld to ${context.last_component}
        And we verify gdk project files
        When we run gdk component build
        When we run gdk test-e2e init
        Then we verify gdk test files
        When we run gdk test-e2e build
        Then we verify the test build files

    @version(min='1.3.0')
    @change_cwd
    Scenario: test-e2e-build-2: As a component builder, when I run the test-e2e build command without building the component, the command exits with an error
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n HelloWorld
        Then command was successful
        And we change directory to HelloWorld
        And change component name to com.example.PythonHelloWorld
        And change artifact uri for all platform from com.example.PythonHelloWorld to ${context.last_component}
        And we verify gdk project files
        When we run gdk test-e2e init
        Then we verify gdk test files
        When we run gdk test-e2e build
        Then cli exited with error
