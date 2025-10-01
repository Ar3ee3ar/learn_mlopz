data "docker_image" "local_image" {
    name = "mlops-project-api"
} 

resource "docker_container" "learn_mlopsz" {
    name = "learn_mlopsz"
    image = data.docker_image.local_image.name

    ports {
        internal = 80
        external = 80
    }
}