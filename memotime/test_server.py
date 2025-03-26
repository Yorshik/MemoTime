from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def load_homepage(self):
        self.client.get("/")

    @task
    def load_sign_up(self):
        self.client.get("/users/signup")

    @task
    def load_login(self):
        self.client.get("/users/login")


