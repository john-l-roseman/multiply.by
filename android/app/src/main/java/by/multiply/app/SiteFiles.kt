package by.multiply.app

import android.content.res.AssetManager
import android.webkit.WebResourceResponse
import java.io.ByteArrayInputStream

/**
 * The pages and files of https://multiply.by bundled in the app, under assets/site/.
 * assets/site/files.txt (written by gather-assets.py) lists every bundled file, one site path
 * per line without the leading slash, for example "train/index.html".
 */
class SiteFiles(private val assets: AssetManager) {

    private val files: Set<String> =
        assets.open("site/files.txt").bufferedReader().useLines { lines ->
            lines.map { it.trim() }.filter { it.isNotEmpty() }.toSet()
        }

    /** The bundled file for a site path: "/" and "/train/" mean their index.html. */
    fun fileFor(path: String?): String? {
        var p = (path ?: "/").removePrefix("/")
        if (p.isEmpty() || p.endsWith("/")) p += "index.html"
        return if (p in files) p else null
    }

    /** True when a path without its trailing slash ("/train") names a bundled folder. */
    fun isFolderWithoutSlash(path: String?): Boolean {
        val p = path ?: return false
        return !p.endsWith("/") && fileFor("$p/") != null
    }

    fun response(path: String?): WebResourceResponse {
        val file = fileFor(path) ?: return notFound()
        val type = mimeType(file)
        val encoding = if (type.startsWith("text/") || type.endsWith("json") ||
            type.endsWith("xml")) "utf-8" else null
        return WebResourceResponse(type, encoding, assets.open("site/$file")).apply {
            // Every response is local; never let the WebView cache a stale copy after an update.
            responseHeaders = mapOf("Cache-Control" to "no-cache")
        }
    }

    fun notFound(): WebResourceResponse {
        val html = """<!doctype html><meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Not in the app</title>
            <body style="font-family:sans-serif;text-align:center;padding:48px 16px;background:#fafaf9">
            <h1 style="font-size:22px">This page is not in the app</h1>
            <p><a href="https://multiply.by/" style="color:#2563eb;font-size:18px">Back to the game</a></p>
            </body>""".trimIndent()
        return WebResourceResponse("text/html", "utf-8", 404, "Not Found",
            mapOf("Cache-Control" to "no-cache"), ByteArrayInputStream(html.toByteArray()))
    }

    private fun mimeType(file: String): String = when (file.substringAfterLast('.', "")) {
        "html", "htm" -> "text/html"
        "txt", "md" -> "text/plain"
        "js" -> "text/javascript"
        "css" -> "text/css"
        "json" -> "application/json"
        "webmanifest" -> "application/manifest+json"
        "png" -> "image/png"
        "jpg", "jpeg" -> "image/jpeg"
        "svg" -> "image/svg+xml"
        "webp" -> "image/webp"
        "mp3" -> "audio/mpeg"
        "ogg" -> "audio/ogg"
        "wav" -> "audio/wav"
        else -> "application/octet-stream"
    }
}
