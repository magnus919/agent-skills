/** Application-owned adapter, not an upstream CryptPad SDK.
 * persist(blob): resolve only after durable save; encrypt client-side if required.
 * compareAndSwapKeys(data): atomically compare data.old, store data.new + data.view,
 *   return the current winning edit key even when another client won the race.
 * report(code): show a visible error without logging document content or keys.
 */
export function createEvents({persist, compareAndSwapKeys, report, setUnsaved}) {
    return {
        onSave(blob, callback) {
            return Promise.resolve().then(() => persist(blob)).then(
                () => callback(),
                () => report('SAVE_FAILED') // No success acknowledgement; upstream may retry.
            );
        },
        onNewKey(data, callback) {
            return Promise.resolve().then(() => compareAndSwapKeys(data)).then(
                key => {
                    if (typeof key !== 'string' || !key) {
                        report('KEY_UPDATE_FAILED');
                        return;
                    }
                    callback(key);
                },
                () => report('KEY_UPDATE_FAILED')
            );
        },
        onHasUnsavedChanges(unsaved) { setUnsaved(unsaved); }
    };
}
