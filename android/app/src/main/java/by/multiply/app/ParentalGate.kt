package by.multiply.app

import android.app.Activity
import android.app.AlertDialog
import android.text.InputType
import android.view.Gravity
import android.view.WindowManager
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.Toast
import kotlin.random.Random

/**
 * Asks a grown-up a sum before anything leaves the app (the browser, the share sheet).
 * The question is a two-digit number times a one-digit number, with the first number from 21 to
 * 29: outside every times table the games teach (up to 20 x 20), easy enough for an adult.
 */
object ParentalGate {

    fun ask(activity: Activity, onPass: () -> Unit) {
        if (activity.isFinishing) return
        val a = Random.nextInt(21, 30)
        val b = Random.nextInt(3, 10)
        val input = EditText(activity).apply {
            inputType = InputType.TYPE_CLASS_NUMBER
            gravity = Gravity.CENTER
            textSize = 24f
            hint = "?"
        }
        val pad = (24 * activity.resources.displayMetrics.density).toInt()
        val box = FrameLayout(activity).apply {
            setPadding(pad, pad / 2, pad, 0)
            addView(input)
        }
        val dialog = AlertDialog.Builder(activity)
            .setTitle("Ask a grown-up")
            .setMessage("This opens another app. What is $a × $b?")
            .setView(box)
            .setPositiveButton("OK") { _, _ ->
                if (input.text.toString().trim() == (a * b).toString()) onPass()
                else Toast.makeText(activity, "Not quite", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .create()
        dialog.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE)
        dialog.show()
        input.requestFocus()
    }
}
