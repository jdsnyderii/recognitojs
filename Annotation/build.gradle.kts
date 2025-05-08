

plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.ktor)
}

group = "com.acme"
version = "1.0.0"

var ktorVersion = "2.3.9" // Latest stable, not 3.x as that doesn't exist yet
var exposedVersion = "0.48.0" // Current version is correct
var logbackVersion = "1.5.3" // Latest stable from 1.5.x series
var sqliteVersion = "3.45.1.0" // Latest stable

application {
    mainClass = "io.ktor.server.netty.EngineMain"

    val isDevelopment: Boolean = project.ext.has("development")
    applicationDefaultJvmArgs = listOf("-Dio.ktor.development=$isDevelopment")
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("io.ktor:ktor-server-core:${ktorVersion}")
    implementation("io.ktor:ktor-server-netty:${ktorVersion}")
    implementation("io.ktor:ktor-server-content-negotiation:${ktorVersion}")
    implementation("io.ktor:ktor-serialization-kotlinx-json:${ktorVersion}")
    implementation("org.jetbrains.exposed:exposed-core:${exposedVersion}")
    implementation("org.jetbrains.exposed:exposed-dao:${exposedVersion}")
    implementation("org.jetbrains.exposed:exposed-jdbc:${exposedVersion}")
    implementation("org.xerial:sqlite-jdbc:${sqliteVersion}")
    implementation("ch.qos.logback:logback-classic:${logbackVersion}")
}
