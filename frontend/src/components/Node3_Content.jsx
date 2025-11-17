import React from 'react';

export function Node3_Content({ data }) {
    return (
        <div className="content-rewrite-card">
            <h2>{data.title}</h2>
            <p>{data.empower_paragraph}</p>
            <h3>Why Choose This Course:</h3>
            <ul>
                {data.why_choose_points.map((point, i) => (
                    <li key={i}>{point}</li>
                ))}
            </ul>
            <div className="content-footer">
                <span className="seo-score">SEO Score: {data.seo_score}/100</span>
                {/* We omit the dropdowns and buttons as they are not functional yet */}
            </div>
        </div>
    );
}