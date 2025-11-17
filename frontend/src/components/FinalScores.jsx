import React from 'react';

// This is the new standalone Final Scores block
export function FinalScores({ data }) {
    return (
        <>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>
                Final Ranking & Scores
            </h2>
            <div className="scores-grid">
                <div className="score-card">
                    <h3 className="score-card-title">SEO Score</h3>
                    <div className="score-card-value">{data.final_seo_score}%</div>
                    <div className="score-card-bar">
                        <div className="bar-inner bar-blue" style={{ width: `${data.final_seo_score}%` }}></div>
                    </div>
                </div>

                <div className="score-card">
                    <h3 className="score-card-title">Readability</h3>
                    <div className="score-card-value">{data.final_readability}%</div>
                    <div className="score-card-bar">
                        <div className="bar-inner bar-green" style={{ width: `${data.final_readability}%` }}></div>
                    </div>
                </div>

                <div className="score-card">
                    <h3 className="score-card-title">Engagement Lift</h3>
                    <div className="score-card-value">+{data.engagement_lift}%</div>
                    <div className="score-card-bar">
                        <div className="bar-inner bar-purple" style={{ width: `${data.engagement_lift}%` }}></div>
                    </div>
                </div>

                <div className="score-card">
                    <h3 className="score-card-title">Avg Rank Impr.</h3>
                    <div className="score-card-value">+{data.avg_rank_improvement}%</div>
                    <div className="score-card-bar">
                        {/* No bar for this one */}
                    </div>
                </div>
            </div>
        </>
    );
}