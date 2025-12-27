import { X } from 'lucide-react';
import './AboutUsModal.css';

const AboutUsModal = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close-btn" onClick={onClose}>
                    <X size={24} />
                </button>

                <div className="modal-header">
                    <div className="university-info">
                        <h2>NATIONAL UNIVERSITY OF TECHNOLOGY</h2>
                        <p>Main I.J.P Road, Sector I-12 Islamabad</p>
                    </div>
                </div>

                <div className="project-title-section">
                    <h3>CS4505 Natural Language Processing</h3>
                </div>

                <div className="project-details-grid">
                    <div className="detail-item">
                        <span className="label">Instructor Name:</span>
                        <span className="value">Lec. Saima Yasmeen</span>
                    </div>
                    <div className="detail-item">
                        <span className="label">Department:</span>
                        <span className="value">Computer Science</span>
                    </div>
                    <div className="detail-item">
                        <span className="label">Batch:</span>
                        <span className="value">CS 2022</span>
                    </div>
                    <div className="detail-item">
                        <span className="label">Assessment Type:</span>
                        <span className="value">PBL</span>
                    </div>
                    <div className="detail-item">
                        <span className="label">Session:</span>
                        <span className="value">Fall-25</span>
                    </div>
                    <div className="detail-item">
                        <span className="label">Due Date:</span>
                        <span className="value">30/12/2025</span>
                    </div>
                </div>

                <div className="group-members-section">
                    <h4>Group Members</h4>
                    <div className="members-table">
                        <div className="member-row header">
                            <span>Name</span>
                            <span>Reg. No</span>
                            <span>Email</span>
                        </div>
                        <div className="member-row">
                            <span>Israr Qayyum</span>
                            <span>F22605004</span>
                            <span>israrqayyumf22@nutech.edu.pk</span>
                        </div>
                        <div className="member-row">
                            <span>Attique Ur Rehman</span>
                            <span>F22605027</span>
                            <span>attiqueurrehmanf22@nutech.edu.pk</span>
                        </div>
                        <div className="member-row">
                            <span>Mehdi Ali</span>
                            <span>F22605005</span>
                            <span>mehdialif22@nutech.edu.pk</span>
                        </div>
                        <div className="member-row">
                            <span>Imran Nadeem</span>
                            <span>F22605030</span>
                            <span>imrannadeemf22@nutech.edu.pk</span>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default AboutUsModal;
