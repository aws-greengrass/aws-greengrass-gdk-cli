Feature: gdk test init works

    @version(min='1.3.0')
    @change_cwd
    Scenario: init test in an existing gdk project
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n test-dir
        Then command was successful
        And we change directory to test-dir
        And change component name to com.example.PythonHelloWorld
        And we verify gdk project files
        When we run gdk test init
        Then we verify gdk test files
