package com.acme

import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.request.*
import io.ktor.http.*
import io.ktor.server.plugins.*

fun Application.configureRouting() {
    routing {
        annotationRoutes(AnnotationService())
    }
}

fun Route.annotationRoutes(annotationService: AnnotationService) {
    route("/api/annotations") {
        get {
            val permalink = call.parameters["permalink"]
            val annotations = if (permalink != null) {
                annotationService.getByPermalink(permalink)
            } else {
                annotationService.getAll()
            }
            call.respond(annotations)
        }

        post {
            val annotation = call.receive<Annotation>()
            val created = annotationService.create(annotation)
            call.respond(HttpStatusCode.Created, created)
        }

        put("/{id}") {
            val id = call.parameters["id"] ?: throw BadRequestException("Missing id")
            val annotation = call.receive<Annotation>()
            val updated = annotationService.update(id, annotation)
            call.respond(updated)
        }

        delete("/{id}") {
            val id = call.parameters["id"] ?: throw BadRequestException("Missing id")
            annotationService.delete(id)
            call.respond(HttpStatusCode.NoContent)
        }
    }
}