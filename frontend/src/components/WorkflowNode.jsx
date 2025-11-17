import React, { useState } from 'react';

export function WorkflowNode({ icon, title, children }) {
    const [isOpen, setIsOpen] = useState(true);

    return (
        <div className="workflow-node">
            <div className="node-header" onClick={() => setIsOpen(!isOpen)}>
                <div className="node-icon">{icon}</div>
                <h2 className="node-title">{title}</h2>
                <span className="node-status"> </span>
                <span className="node-toggle">{isOpen ? '▲' : '▼'}</span>
            </div>
            {isOpen && (
                <div className="node-body">
                    {children}
                </div>
            )}
        </div>
    );
}