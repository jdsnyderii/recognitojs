package com.acme

import `import org`.jetbrains.exposed.sql.selectAll
import org.jetbrains.exposed.sql.*
import kotlinx.coroutines.Dispatchers
import org.jetbrains.exposed.sql.selectAll
import org.jetbrains.exposed.sql.transactions.transaction
import kotlin.coroutines.CoroutineContext

class AnnotationService {
    object DatabaseFactory {
        private val dispatcher: CoroutineContext = Dispatchers.IO

        suspend fun <T> dbQuery(block: () -> T): T =
            kotlinx.coroutines.withContext(dispatcher) {
                transaction { block() }
            }
    }
    suspend fun getAll(): List<Annotation> = DatabaseFactory.dbQuery {
        Annotations.selectAll().map { it.toAnnotation() }
    }

    suspend fun getByPermalink(permalink: String): List<Annotation> = DatabaseFactory.dbQuery {
        Annotations.selectAll().where { Annotations.permalink eq permalink }.map { it.toAnnotation() }
    }

    suspend fun create(annotation: Annotation): Annotation = DatabaseFactory.dbQuery {
        Annotations.insert {
            it[id] = annotation.id
            it[user] = annotation.user
            it[permalink] = annotation.permalink
            it[annotation] = annotation.annotation
            it[version] = annotation.version
        }
        annotation
    }

    suspend fun update(id: String, annotation: Annotation): Annotation = DatabaseFactory.dbQuery {
        Annotations.update({ Annotations.id eq id }) {
            it[user] = annotation.user
            it[permalink] = annotation.permalink
            it[annotation] = annotation.annotation
            it[version] = annotation.version
        }
        annotation
    }

    suspend fun delete(id: String) = DatabaseFactory.dbQuery {
        Annotations.deleteWhere { Annotations.id eq id }
    }
}