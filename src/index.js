import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

const ORIGIN = window.location.origin;
const STATUS_ENDPOINT = ORIGIN + '/status';
const ACTIVATE_ENDPOINT = ORIGIN + '/actions/activate';
const DEACTIVATE_ENDPOINT = ORIGIN + '/actions/deactivate';
const RESCAN_ENDPOINT = ORIGIN + '/actions/rescan';

const DEFAULT_ACTIVATION_TIMEOUT = 3600;

class Main extends React.Component {

    status = setInterval(() =>  {fetch(STATUS_ENDPOINT)
        .then(response => response.json())
        .then(data => this.setState({ status: data.status }))
        .catch((error) => console.error(error));}, 1000);

    constructor(props) {
        super(props);
        this.state = {
            status: "NOT CONNECTED",
            activationTimeoutSeconds: DEFAULT_ACTIVATION_TIMEOUT
        };
        this.activationTimeoutChangeHandler = this.activationTimeoutChangeHandler.bind(this);
    }

    activationTimeoutChangeHandler(event) {
        this.setState({
            activationTimeoutSeconds: event.target.value
        })
    }

    render() {
        return (
            <>
                <h1>Status: {this.state.status}</h1>
                <br />
                <ActionButton label={"ACTIVATE"} action={() => actionActivate(this.state.activationTimeoutSeconds)} disabled={this.state.status !== 'DEACTIVATED'}/>
                <br />
                <ActionButton label={"DEACTIVATE"} action={() => actionDeactivate()} disabled={this.state.status !== 'ACTIVATED'}/>
                <br />
                <ActionButton label={"RESCAN"} action={() => actionRescan()} disabled={this.state.status !== 'ACTIVATED'}/>
                <br />
                <ActivationTimeoutForm activationTimeoutChangeHandler={this.activationTimeoutChangeHandler} />
            </>
        );
    }
}

class ActionButton extends React.Component {
    render() {
        return (
            <button onClick={this.props.action} disabled={this.props.disabled}>{this.props.label}</button>
        )
    }
}

class ActivationTimeoutForm extends React.Component {
    render() {
        return (
            <form>
                <label>
                    Activation Timeout (Seconds):
                    <input type="number" defaultValue={DEFAULT_ACTIVATION_TIMEOUT} onChange={this.props.activationTimeoutChangeHandler} />
                </label>
            </form>
        );
    }
}

function actionActivate(timeoutSeconds) {
    executeAndLogGetRequest(ACTIVATE_ENDPOINT + '?timeout_seconds=' + timeoutSeconds);
}

function actionDeactivate() {
    executeAndLogGetRequest(DEACTIVATE_ENDPOINT);
}

function actionRescan() {
    executeAndLogGetRequest(RESCAN_ENDPOINT);
}

function executeAndLogGetRequest(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => console.log(data))
        .catch((error) => console.error(error));
}

// ========================================

ReactDOM.render(
    <Main />,
    document.getElementById('root')
);
