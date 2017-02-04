import React from 'react';
import { RIEInput } from 'riek';
import _ from 'lodash';

class NameEdit extends React.Component {
  constructor(props) {
    super(props);
    this.dataChange = this.dataChange.bind(this);
    this.validatePeripheralName = this.validatePeripheralName.bind(this);
  }

  componentDidMount() {
    // MAJOR HAXORS! The default RIEInput component trims spaces from the
    // end of strings before passing to validation. But we need
    // to check for those spaces. So here I am modifying the RIEInput
    // component's textChanged function to not trim before validation.
    this.nameEdit.textChanged = (event) => {
      this.nameEdit.doValidations(event.target.value);
    };
  }

  shouldComponentUpdate(nextProps) {
    // By default, the component is constantly being updated which makes
    // the RIEInput unusable. This prevents unnecessary updating.
    return nextProps.name !== this.props.name;
  }

  dataChange(data) {
    console.log('Deprecated: dataChange in NameEdit:');
    console.log(data);
  }

  validatePeripheralName(name) {
    const re = new RegExp('^[A-Za-z][A-Za-z0-9]+$');
    const isValid = re.test(name);
    const allCurrentPeripherals = _.toArray(this.props.peripherals);
    const isDuplicate = _.some(allCurrentPeripherals, (peripheral) => {
      return peripheral.name === name && peripheral.id !== this.props.id;
    });
    return isValid && !isDuplicate;
  }

  render() {
    return (
      <div>
        <RIEInput
          ref={(ref) => { this.nameEdit = ref; }}
          className="static"
          classEditing="editing"
          classInvalid="invalid"
          validate={this.validatePeripheralName}
          value={this.props.name}
          change={this.dataChange}
          propName="name"
        />
      </div>
    );
  }
}

NameEdit.propTypes = {
  name: React.PropTypes.string.isRequired,
  id: React.PropTypes.string.isRequired,
  peripherals: React.PropTypes.object.isRequired,
};

export default NameEdit;
