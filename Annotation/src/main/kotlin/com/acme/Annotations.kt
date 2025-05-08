package com.acme

import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.Column

object Annotations : Table() {
    val id: Column<String> = varchar("id", 128)

    val user: Column<String> = varchar("user", 255)
    val permalink: Column<String> = varchar("permalink", 255)
    val annotation: Column<String> = json("annotation")
    val version: Column<String> = varchar("version", 64)

    override val primaryKey: PrimaryKey = PrimaryKey(id, name = "PK_Annotation_ID")
}