import React from 'react';
import { Modal } from 'react-bootstrap';

const PreferencesBox = (props) => (
  <Modal show={props.showModal} onHide={props.closeModal}>
    <Modal.Header closeButton>
      <Modal.Title>Preferences</Modal.Title>
    </Modal.Header>
    <Modal.Body>
      Placeholder
    </Modal.Body>
  </Modal>
);

PreferencesBox.propTypes = {
  showModal: React.PropTypes.bool,
  closeModal: React.PropTypes.func,
};

export default PreferencesBox;
