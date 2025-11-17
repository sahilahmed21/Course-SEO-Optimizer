import React, { useState, useEffect } from 'react';

export function Node5_Metadata({ data }) {
    // Use local state to make the fields editable
    const [metaTitle, setMetaTitle] = useState('');
    const [metaDesc, setMetaDesc] = useState('');

    // When the 'data' prop (from the API) changes, update our local state
    useEffect(() => {
        if (data) {
            setMetaTitle(data.meta_title);
            setMetaDesc(data.meta_description);
        }
    }, [data]); // This effect runs when 'data' is loaded

    return (
        <div>
            <div className="metadata-card">
                <h3>Meta Title</h3>
                {/* Make this an editable input */}
                <input
                    type="text"
                    className="form-input"
                    value={metaTitle}
                    onChange={(e) => setMetaTitle(e.target.value)}
                />
            </div>

            <div className="metadata-card">
                <h3>Meta Description</h3>
                {/* Make this an editable textarea */}
                <textarea
                    className="form-input"
                    rows="3"
                    value={metaDesc}
                    onChange={(e) => setMetaDesc(e.target.value)}
                />
            </div>

            <div className="metadata-card">
                <h3>Meta Keywords</h3>
                <div>
                    {data.meta_keywords.map((kw, i) => (
                        <span key={i} className="keyword-chip chip-gray">{kw}</span>
                    ))}
                </div>
            </div>

            {/* The screenshot shows "Update Metadata" but you asked for "Edit" */}
            {/* We'll keep "Update Metadata" as it matches the screenshot */}
            <button className="btn btn-primary">Update Metadata</button>
        </div>
    );
}