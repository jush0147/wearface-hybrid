plugins {
    id("com.android.application")
}
android {
    namespace = "dev.local.wear.hybridface"
    compileSdk = 35
    defaultConfig {
        applicationId = "dev.local.wear.hybridface"
        minSdk = 34
        targetSdk = 35
        versionCode = 1
        versionName = "0.1"
    }
    buildTypes {
        getByName("debug") {
            isMinifyEnabled = false
        }
        getByName("release") {
            isMinifyEnabled = false
            isShrinkResources = false
        }
    }
}
