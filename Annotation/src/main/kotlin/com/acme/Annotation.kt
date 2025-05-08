package com.acme

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.jetbrains.exposed.sql.ResultRow


@Serializable
data class Annotation(
    val id: String,
    val user: String,
    val permalink: String,
    val annotation: Json,
    val version: String
)

fun ResultRow.toAnnotation() = Annotation(
    id = this[Annotations.id],
    user = this[Annotations.user],
    permalink = this[Annotations.permalink],
    annotation = this[Annotations.annotation],
    version = this[Annotations.version]
)