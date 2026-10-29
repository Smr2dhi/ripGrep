pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Docker') {
            steps {
                sh 'docker --version'
            }
        }

        stage('Build Backend Image') {
            steps {
                sh 'docker build -t ripgrep-backend -f backend/Dockerfile .'
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh 'docker build -t ripgrep-frontend -f frontend/Dockerfile .'
            }
        }
    }
}
