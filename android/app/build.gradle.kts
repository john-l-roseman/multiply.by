import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "by.multiply.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "by.multiply.app"   // never change after publishing
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "0.1"
    }

    buildFeatures { buildConfig = true }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
}

dependencies {
    implementation("androidx.activity:activity-ktx:1.10.1")
    implementation("androidx.webkit:webkit:1.14.0")
}

// The pages come from gather-assets.py (they are not in the repo): stop with a clear message.
val siteFiles = layout.projectDirectory.file("src/main/assets/site/files.txt")
tasks.named("preBuild") {
    doFirst {
        if (!siteFiles.asFile.exists()) {
            throw GradleException(
                "The games are missing: run  python3 gather-assets.py  in the android folder first.")
        }
    }
}
