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

        stage('Delete Backend Image') {
            steps {
                sh 'docker rm -f greprag-backend'
            }
        }
// Testing automatic SCM polling
        stage('delete Frontend Image') {
            steps {
                sh 'docker rm -f greprag-frontend'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'gemini-api-key',
                        variable: 'GEMINI_API_KEY'
                    )
                ]) {
                    sh '''
                        set -eu

                        docker compose config --quiet
                        docker compose up -d --build
                        docker compose ps
                    '''
                }
            }
        }
    }
}
