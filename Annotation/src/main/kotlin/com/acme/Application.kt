package com.acme

import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.*
import io.ktor.server.netty.EngineMain
import io.ktor.server.http.content.*
import io.ktor.server.routing.*
import io.ktor.server.plugins.contentnegotiation.*
import org.jetbrains.exposed.sql.Database
import org.jetbrains.exposed.sql.SchemaUtils
import org.jetbrains.exposed.sql.transactions.transaction

fun main(args: Array<String>) {
    EngineMain.main(args)
}

fun Application.module() {
    Database.connect("jdbc:sqlite:annotations.db", driver = "org.sqlite.JDBC")

    transaction {
        SchemaUtils.create(Annotations)
    }


    val annotationService = AnnotationService()

    install(ContentNegotiation) {
        json()
    }

    configureRouting()
    configureStaticResources()
}

fun Application.configureStaticResources() {
    routing {
        staticResources("/static", basePackage = "static") {
        }
    }
}

