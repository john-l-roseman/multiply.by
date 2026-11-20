package by.multiply.app

import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import org.json.JSONObject

/**
 * One full-screen WebView showing the multiply.by games from the app's own files, at their real
 * addresses (https://multiply.by/...), so the pages run unchanged: their links, localStorage and
 * SOURCE's prompt.txt work as on the website. Anything not bundled (About, Build It, other sites,
 * sharing) leaves the app only after the parental gate.
 */
class MainActivity : ComponentActivity() {

    private lateinit var web: WebView
    private lateinit var site: SiteFiles

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        site = SiteFiles(assets)
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)

        // Draw edge to edge (required from Android 15) and pad the page clear of the system bars.
        WindowCompat.setDecorFitsSystemWindows(window, false)
        WindowCompat.getInsetsController(window, window.decorView).apply {
            isAppearanceLightStatusBars = true
            isAppearanceLightNavigationBars = true
        }
        val root = FrameLayout(this).apply { setBackgroundColor(Color.parseColor("#FAFAF9")) }
        ViewCompat.setOnApplyWindowInsetsListener(root) { v, insets ->
            val bars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            WindowInsetsCompat.CONSUMED
        }

        web = WebView(this)
        root.addView(web, FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))
        setContentView(root)

        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = false
            allowContentAccess = false
            setSupportMultipleWindows(false)   // target="_blank" links open in this WebView
        }
        web.webViewClient = Client()
        setUpShare()

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (web.canGoBack()) web.goBack()
                else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                    isEnabled = true
                }
            }
        })

        if (savedInstanceState == null || web.restoreState(savedInstanceState) == null) {
            web.loadUrl(HOME)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }

    private inner class Client : WebViewClient() {

        override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
            val url = request.url
            if (isSite(url)) {
                if (site.fileFor(url.path) != null) return false      // bundled: load it here
                if (site.isFolderWithoutSlash(url.path)) {             // "/train" -> "/train/"
                    view.loadUrl(url.buildUpon().path(url.path + "/").build().toString())
                    return true
                }
            }
            if (!request.isForMainFrame) return true
            // Not bundled (About, Build It, other sites, mailto:, ...): the browser, after the gate.
            ParentalGate.ask(this@MainActivity) { openOutside(url) }
            return true
        }

        override fun shouldInterceptRequest(
            view: WebView, request: WebResourceRequest
        ): WebResourceResponse? {
            val url = request.url
            // Pages, prompt.txt, pictures, pwa.js: all from the app. /sw.js is not bundled and
            // gets a 404, so no service worker is installed (none is needed offline-first).
            if (isSite(url)) return site.response(url.path)
            // Nothing else is ever fetched: the pages are self-contained.
            return site.notFound()
        }
    }

    private fun isSite(url: Uri): Boolean =
        (url.scheme == "https" || url.scheme == "http") && url.host == "multiply.by"

    private fun openOutside(url: Uri) {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, url).addCategory(Intent.CATEGORY_BROWSABLE))
        } catch (e: ActivityNotFoundException) {
            Toast.makeText(this, "No app can open this link", Toast.LENGTH_SHORT).show()
        }
    }

    /**
     * WebView has no navigator.share. Give the pages one that hands the text to Android's share
     * sheet (after the parental gate), so the games take their phone path (layout.txt: SHARE THE
     * SITE) instead of copying the link.
     */
    private fun setUpShare() {
        if (!WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) return
        val origins = setOf(ORIGIN)
        WebViewCompat.addWebMessageListener(web, "MultiplyApp", origins) { _, message, _, isMainFrame, _ ->
            if (!isMainFrame) return@addWebMessageListener
            val data = try { JSONObject(message.data ?: "") } catch (e: Exception) { return@addWebMessageListener }
            val link = data.optString("url")
            val text = data.optString("text").let {   // the games' text already ends with the link
                if (link.isBlank() || it.contains(link)) it else listOf(it, link).filter { s -> s.isNotBlank() }.joinToString("\n")
            }
            if (text.isBlank()) return@addWebMessageListener
            ParentalGate.ask(this) {
                val send = Intent(Intent.ACTION_SEND).apply {
                    type = "text/plain"
                    putExtra(Intent.EXTRA_TEXT, text)
                    data.optString("title").takeIf { it.isNotBlank() }
                        ?.let { putExtra(Intent.EXTRA_SUBJECT, it) }
                }
                startActivity(Intent.createChooser(send, null))
            }
        }
        if (WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            WebViewCompat.addDocumentStartJavaScript(web, SHARE_SCRIPT, origins)
        }
    }

    companion object {
        const val ORIGIN = "https://multiply.by"
        const val HOME = "https://multiply.by/"
        const val SHARE_SCRIPT = """
            (function () {
              if (!window.MultiplyApp) return;
              navigator.share = function (d) {
                d = d || {};
                MultiplyApp.postMessage(JSON.stringify(
                  { title: d.title || '', text: d.text || '', url: d.url || '' }));
                return Promise.resolve();
              };
              navigator.canShare = function () { return true; };
            })();
        """
    }
}
