import React, { useState } from "react";
import axios from "../../api/axios";
import { toast } from "react-hot-toast";

export default function FeedbackSettings() {
  const [rating, setRating] = useState(0);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) return toast.error("Please select a rating");
    if (!message.trim()) return toast.error("Please write a message");

    setLoading(true);
    try {
        await axios.post("/feedback/", { rating, message });
        toast.success("Thank you for your feedback!");
        setRating(0);
        setMessage("");
    } catch (err) {
        console.error(err);
        toast.error("Failed to submit feedback");
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm text-center max-w-2xl mx-auto">
        <div className="w-16 h-16 bg-sky-100 text-sky-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">💌</span>
        </div>
        <h2 className="text-2xl font-bold text-slate-900">We value your feedback!</h2>
        <p className="text-slate-500 mt-2 mb-6">Help us improve your ERP experience. Found a bug or have a feature request?</p>

        <div className="flex justify-center gap-2 mb-6">
            {[1, 2, 3, 4, 5].map((star) => (
                <button 
                    key={star} 
                    onClick={() => setRating(star)}
                    className={`text-4xl transition-transform hover:scale-110 ${rating >= star ? "text-amber-400" : "text-slate-200"}`}
                >
                    ★
                </button>
            ))}
        </div>

        <textarea 
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full border-slate-200 rounded-xl p-4 bg-slate-50 focus:ring-sky-400 min-h-[120px] mb-4"
            placeholder="Tell us what you think..."
        ></textarea>

        <button 
            onClick={handleSubmit}
            disabled={loading}
            className="bg-slate-900 text-white px-8 py-3 rounded-xl hover:bg-slate-800 shadow-lg shadow-slate-900/20 w-full font-bold disabled:opacity-70"
        >
            {loading ? "Submitting..." : "Submit Feedback"}
        </button>
    </div>
  );
}